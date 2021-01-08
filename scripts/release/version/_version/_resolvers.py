from abc import ABC, abstractmethod
from collections import namedtuple
import re
from typing import ClassVar, Collection, Optional

from git import Repo
from semver import Version

from ._config import FEATURE, DEVELOP, RELEASE, MASTER, HOTFIX, DETACHED_HEAD
from ._providers import IVersionProvider
from ._stages import get_stage, to_next_stage, Stage


SPECIAL_BRANCHES = {FEATURE, DEVELOP, RELEASE, MASTER, HOTFIX}
v0_0_0 = Version(0, 0, 0)


StageInfo = namedtuple("StageInfo", ("branch", "is_full_name", "stage"))


class VersionResolutionError(ValueError):
    pass


class IVersionResolver(ABC):
    """
    Responsible for resolving the version of the package. No assumption is made on where/how versions are stored. They
    are provided to the resolver.
    """

    def __init__(self, version_provider: IVersionProvider):
        self._provider = version_provider

    @abstractmethod
    def resolve_version(self) -> Optional[Version]:
        """
        Resolves the version of a package based on the latest available version of the package.
        """ ""
        raise NotImplementedError()


class BranchBasedVersionResolver(IVersionResolver, ABC):
    """
    Resolve the package version based on the branch on which the current commit resides.
    """

    branch_to_stage: ClassVar[Collection[StageInfo]] = []
    disallow_special_branch_names_without_stage: ClassVar[bool] = True

    def __init__(self, version_provider: IVersionProvider, repo: Repo):
        super().__init__(version_provider)
        self._commit_sha = repo.head.commit.hexsha
        self._branch = self.get_branch_name(repo)
        self._stage = self.get_stage_from_branch(self._branch)

    @classmethod
    def get_branch_name(cls, repo: Repo) -> str:
        return DETACHED_HEAD if repo.head.is_detached else repo.head.ref.name

    @classmethod
    def get_stage_from_branch(cls, branch: str) -> Optional[Stage]:
        branch_root = branch.split("/")[0]
        stage_info = next((stage_info for stage_info in cls.branch_to_stage if stage_info.branch == branch_root), None)

        if stage_info:
            if stage_info.is_full_name and branch != stage_info.branch:
                raise VersionResolutionError(
                    f"Branch with name {branch} starts with {branch_root}/ but is not {branch_root}. "
                    f"This is not allowed."
                )
            return stage_info.stage

        if cls.disallow_special_branch_names_without_stage and branch_root in SPECIAL_BRANCHES:
            raise VersionResolutionError(
                f"{branch_root} has a special meaning but is not part of your release logic. This is not allowed. "
                f"Special branches: {SPECIAL_BRANCHES}."
            )

        return None

    @property
    def branch(self) -> str:
        return self._branch

    @property
    def stage(self) -> Optional[Stage]:
        return self._stage

    @abstractmethod
    def resolve_version(self) -> Optional[Version]:
        if not self.stage:
            return self._provider.get_current_version()

        if self.branch == DETACHED_HEAD:
            raise NotImplementedError(
                f"{type(self).__name__} does not implement logic to resolve the version of a detached head."
            )

        if self.stage:
            # NOTE: we assume idempotency here. If the package was already versioned with a version consistent with the
            # current stage or higher, we just return it.
            current_version = self._provider.get_current_version()
            if current_version and get_stage(current_version) == self.stage:
                return current_version

        return None


class ContinuousDeploymentVersionResolver(BranchBasedVersionResolver):
    f"""
    In Continuous Deployment developers commit to the {DEVELOP} branch. On successful test of the commit the branch is
    merged to the {MASTER} branch and the package is released. There is no {FEATURE} or {HOTFIX} branch.
    """

    branch_to_stage: ClassVar[Collection[StageInfo]] = [
        StageInfo(FEATURE, False, Stage.ALPHA),
        StageInfo(DEVELOP, True, Stage.ALPHA),
        StageInfo(MASTER, True, Stage.RELEASE),
    ]

    def resolve_version(self) -> Optional[Version]:
        base_version = super().resolve_version()
        if base_version:
            return base_version
        if not self.stage:
            return None

        latest_version = self._provider.get_latest_version()
        if self.stage == Stage.RELEASE:
            if latest_version is None:
                return v0_0_0
            if get_stage(latest_version) is Stage.RELEASE:
                return latest_version.next_minor
        return to_next_stage(latest_version or v0_0_0, self.stage, self._commit_sha)


class GitFlowReleaseVersionResolver(BranchBasedVersionResolver):
    f"""
    GitFlow releases are started by creating a {RELEASE} branch following the pattern defined by the attribute
    release_branch_pattern. Bugs found in testing lead to new release candidates on the {RELEASE} branch.
    Once the package is ready to be released, the {RELEASE} branch is merged with the {MASTER} branch.
    Any bug found in the software released is committed directly on the {MASTER} branch or on a {HOTFIX} branch
    created from the {MASTER} branch which is merged back to {MASTER} once the bug is fixed.
    """

    branch_to_stage: ClassVar[Collection[StageInfo]] = [
        StageInfo(FEATURE, False, Stage.ALPHA),
        StageInfo(DEVELOP, True, Stage.ALPHA),
        StageInfo(RELEASE, False, Stage.RELEASE_CANDIDATE),
        StageInfo(MASTER, True, Stage.RELEASE),
        StageInfo(HOTFIX, False, Stage.POST),
    ]
    release_branch_pattern: ClassVar[re.Pattern] = re.compile(r"^({rel}/v(?P<version>\d.\d))$".format(rel=RELEASE))

    def __init__(self, version_provider: IVersionProvider, repo: Repo):
        super().__init__(version_provider, repo)
        self._release_candidate_version = self.get_latest_candidate_version(repo)

    @classmethod
    def get_latest_candidate_version(cls, repo: Repo) -> Optional[Version]:
        max_version = None
        for branch in repo.heads:
            version = cls.get_version(branch.name)
            if version is not None and max_version is not None:
                max_version = max(max_version, version)
            else:
                max_version = version
        return max_version

    @classmethod
    def get_version(cls, branch: str) -> Optional[Version]:
        match = cls.release_branch_pattern.match(branch)
        if match:
            version = Version.parse(f"{match.group('version')}.0")
            return version
        return None

    def resolve_version(self) -> Optional[Version]:
        base_version = super().resolve_version()
        if base_version:
            return base_version
        if not self.stage:
            return None

        if self.stage is Stage.ALPHA:

            # NOTE: super().resolve_version() ensures that if the current version is of the right stage it is returned
            # early. There is an extra case to handle for ALPHA release: if a new release candidate branch has been
            # created from the current commit. In that case we should return the release candidate version.
            current_version = self._provider.get_current_version()
            if current_version and get_stage(current_version) == Stage.RELEASE_CANDIDATE:
                return current_version

            # we make use of the version derived from the latest release branch and the latest version returned by the
            # provider. This helps cater for cases where release branches are deleted on complete release and cases
            # where the first release candidate build failed and a version was never committed.
            latest_version = self._provider.get_latest_version() or v0_0_0
            if self._release_candidate_version:
                latest_version = max(latest_version, self._release_candidate_version)
            return to_next_stage(latest_version, self.stage, self._commit_sha)

        if self.stage is Stage.RELEASE_CANDIDATE:
            release_version = self.get_version(self.branch)
            if release_version is None:
                raise VersionResolutionError(
                    f"The release branch you created has the wrong format: {self.branch}. The regex pattern for "
                    f"a release branch is {self.release_branch_pattern.pattern}."
                )
            latest_version = self._provider.get_latest_version() or v0_0_0
            if release_version == latest_version.stable:
                return to_next_stage(latest_version, self.stage, self._commit_sha)
            elif release_version in {latest_version.next_minor, latest_version.next_major}:
                return to_next_stage(release_version.first_prerelease, self.stage, self._commit_sha)
            elif release_version < latest_version.stable:
                raise VersionResolutionError(
                    f"You have created a new release branch: {self.branch} for an old release. The latest release "
                    f"candidate version is: {latest_version}."
                )
            raise VersionResolutionError(
                f"Release candidate version {release_version} is not a stable version above the current one: "
                f"{latest_version}."
            )

        release_stages = {
            Stage.RELEASE: (Stage.POST, Stage.RELEASE, Stage.RELEASE_CANDIDATE),
            Stage.POST: (Stage.POST, Stage.RELEASE),
        }
        if self.stage in release_stages:
            latest_version = self._provider.get_latest_version()
            if latest_version is None:
                if self.stage is Stage.RELEASE:
                    return v0_0_0
                raise VersionResolutionError(
                    "It is not possible to start a hotfix before a release has ever been made."
                )

            transition_from = release_stages[self.stage]
            latest_version_stage = get_stage(latest_version)
            if latest_version_stage in transition_from:
                return to_next_stage(latest_version, self.stage, self._commit_sha)
            raise VersionResolutionError(
                f"The version: {latest_version} has stage: {latest_version_stage.name} which cannot be used for "
                f"release. Valid stages are: {[stage.name for stage in transition_from]}"
            )

        raise NotImplementedError(f"Version resolution was not implemented for stage: {self.stage.name}.")
