from abc import ABC, abstractmethod
from typing import Optional

from git import Repo
from semver import Version

from ._tags import get_versions
from ._stages import Stage, get_stage

__all__ = [
    "IVersionProvider",
    "ProvideVersionError",
    "VersionProviderFromTags",
    "VersionProviderFromTagsVisibleFromCommit",
]


class ProvideVersionError(ValueError):
    pass


class IVersionProvider(ABC):
    """
    Exposes retrieval of the latest version of a package.
    """

    @abstractmethod
    def get_current_version(self) -> Optional[Version]:
        """
        Returns the current version of the package if it is versioned or otherwise None
        """
        raise NotImplementedError()

    @abstractmethod
    def get_latest_version(self, in_stage: Optional[Stage] = None) -> Optional[Version]:
        """
        Retrieves the latest version of a package in a given stage (f.ex. the latest release or latest release
        candidate).
        Returns None if no version of the package was ever produced.
        """
        raise NotImplementedError()


class VersionProviderFromTags(IVersionProvider):
    """
    This provider can be used if versions are stamped in a repository via git tags.
    The versions are fixed on provider instantiation to ensure consistency.
    """

    def __init__(self, repo: Repo):
        self._all_versions = get_versions(repo)
        self._current_versions = get_versions(repo, lambda tag, _: repo.head.commit == tag.commit)

    def get_current_version(self) -> Optional[Version]:
        return max(self._current_versions) if self._current_versions else None

    def get_latest_version(self, in_stage: Optional[Stage] = None) -> Optional[Version]:
        return max((vs for vs in self._all_versions if (get_stage(vs) is in_stage if in_stage else True)), default=None)


class VersionProviderFromTagsVisibleFromCommit(IVersionProvider):
    """
    This provider can be used if versions are stamped in a repository via git tags.
    The versions are fixed on provider instantiation to ensure consistency.
    This provider only considers commits that are visible from the current commit.
    """

    def __init__(self, repo: Repo):
        self._all_versions = get_versions(
            repo, lambda tag, _: tag.commit in repo.merge_base(tag.commit, repo.head.commit)
        )
        self._current_versions = get_versions(repo, lambda tag, _: repo.head.commit == tag.commit)

    def get_current_version(self) -> Optional[Version]:
        return max(self._current_versions) if self._current_versions else None

    def get_latest_version(self, in_stage: Optional[Stage] = None) -> Optional[Version]:
        return max(self._all_versions) if self._all_versions else None
