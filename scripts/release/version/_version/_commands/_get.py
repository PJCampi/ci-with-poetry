from typing import Optional

from git import Repo
from poetry.core.semver import Version

from .._config import CONTINUOUS_DEPLOYMENT
from .._providers import IVersionProvider, VersionProviderFromTags, VersionProviderFromTagsVisibleFromCommit
from .._resolvers import IVersionResolver, GitFlowReleaseVersionResolver, ContinuousDeploymentVersionResolver
from .._stages import get_stage, Stage

__all__ = ["get_version"]


def get_version(repo: Repo, *, infer: bool = False, include_alpha: bool = False) -> Optional[Version]:

    if CONTINUOUS_DEPLOYMENT:
        provider: IVersionProvider = VersionProviderFromTags(repo)
        resolver: IVersionResolver = ContinuousDeploymentVersionResolver(provider, repo)
    else:
        provider = VersionProviderFromTagsVisibleFromCommit(repo)
        resolver = GitFlowReleaseVersionResolver(provider, repo)

    version = resolver.resolve_version() if infer else provider.get_current_version()
    if version and not include_alpha and get_stage(version) is Stage.ALPHA:
        return None

    return version
