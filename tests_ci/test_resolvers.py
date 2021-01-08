from typing import Optional, Union
from unittest.mock import Mock, patch

import pytest
from semver import Version

from scripts.release.version._version._resolvers import (
    GitFlowReleaseVersionResolver, ContinuousDeploymentVersionResolver, VersionResolutionError
)
from .fixtures import DummyVersionProvider


@pytest.mark.parametrize(
    "branch_name, latest_version, current_version, expected",
    [
        pytest.param("develop", "", "", "0.1.0-alpha+0", id="first-commit"),
        pytest.param("develop", "0.1.0-alpha+0", "0.1.0-alpha+0", "0.1.0-alpha+0", id="first-commit-tagged"),
        pytest.param("feature/my-feature", "", "0.1.0-alpha+0", "0.1.0-alpha+0", id="feature"),
        pytest.param("develop", "0.0.0", "", "0.1.0-alpha+0", id="first-commit-with-initial-version"),
        pytest.param("master", "", "", "0.0.0", id="first-commit-master"),
        pytest.param("master", "0.0.0", "0.0.0", "0.0.0", id="first-commit-master-tagged"),
        pytest.param("master", "0.0.0", "", "0.0.1", id="first-patch"),
        pytest.param("release/v0.0", "0.1.0-alpha+0", "", VersionResolutionError(), id="first-release-too-low"),
        pytest.param("release/v0.2", "0.1.0-alpha+0", "", VersionResolutionError(), id="first-release-too-high"),
        pytest.param("release/v0.1.1", "0.0.0", "", VersionResolutionError(), id="first-release-wrong-format"),
        pytest.param("release/v0.1", "0.1.0-alpha+0", "", "0.1.0-rc1", id="first-release-candidate"),
        pytest.param("release/v0.1", "0.1.0-rc1", "0.1.0-rc1", "0.1.0-rc1", id="first-release-candidate-tagged"),
        pytest.param("develop", "0.1.0-rc1", "0.1.0-rc1", "0.1.0-rc1", id="develop-release-candidate-tagged"),
        pytest.param("release/v0.1", "0.1.0-rc1", "", "0.1.0-rc2", id="first-release-another-candidate"),
        pytest.param("develop", "0.1.0-rc1", "", "0.2.0-alpha+0", id="another-develop-version"),
        pytest.param("develop", "0.2.0-alpha+0", "0.2.0-alpha+0", "0.2.0-alpha+0", id="another-develop-tagged"),
        pytest.param("master", "0.1.0-rc2", "", "0.1.0", id="first-release-successful"),
        pytest.param("master", "0.1.0", "0.1.0", "0.1.0", id="first-release-successful-tagged"),
        pytest.param("master", "0.1.0", "", "0.1.1", id="first-release-patch"),
        pytest.param("master", "0.1.1", "0.1.1", "0.1.1", id="first-release-patch-tagged"),
        pytest.param("master", "0.3.0-rc1", "", "0.3.0", id="release-after-botched-one"),
        pytest.param("random-branch", "0.1.0-rc1", "", None, id="random-branch"),
        pytest.param("hotfix/a", "0.1.0", "0.1.0", "0.1.0+post1", id="hotfix"),
        pytest.param("hotfix/a", "0.1.0+post1", "0.1.0+post1", "0.1.0-post1", id="hotfix-tagged"),
        pytest.param("hotfix/a", "0.1.0+post1", "", "0.1.0+post2", id="hotfix-another"),
        pytest.param("master", "0.1.0+post2", "0.1.0+post2", "0.1.1", id="hotfix-merged-to-master"),
    ],
)
def test_git_flow_release_resolver(
    branch_name: str,
    latest_version: str,
    current_version: str,
    expected: Union[Optional[str], VersionResolutionError],
):
    provider = DummyVersionProvider.from_string(current_version, latest_version)
    with patch(
        "scripts.release.version._version._resolvers.GitFlowReleaseVersionResolver.get_branch_name",
        return_value=branch_name
    ):
        with patch(
            "scripts.release.version._version._resolvers.GitFlowReleaseVersionResolver.get_latest_candidate_version",
            return_value=None
        ):
            repo = Mock(head=Mock(commit=Mock(hexsha="0")))

            if isinstance(expected, VersionResolutionError):
                with pytest.raises(VersionResolutionError):
                    resolver = GitFlowReleaseVersionResolver(provider, repo)
                    resolver.resolve_version()
            else:
                expected_version = Version.parse(expected) if expected else None
                resolver = GitFlowReleaseVersionResolver(provider, repo)
                assert resolver.resolve_version() == expected_version


@pytest.mark.parametrize(
    "branch_name, latest_version, current_version, expected",
    [
        pytest.param("develop", "", "", "0.1.0-alpha+0", id="first-commit"),
        pytest.param("develop", "0.1.0-alpha+0", "0.1.0-alpha+0", "0.1.0-alpha+0", id="first-commit-tagged"),
        pytest.param("feature/my-feature", "0.1.0-alpha+0", "", "0.1.0-alpha+0", id="feature"),
        pytest.param("master", "0.1.0-alpha+0", "", "0.1.0", id="first-release-successful"),
        pytest.param("master", "0.1.0", "0.1.0", "0.1.0", id="first-release-tagged"),
        pytest.param("develop", "0.1.0", "", "0.2.0-alpha+0", id="another-develop-commit"),
        pytest.param("hotfix", "", "0.1.0", VersionResolutionError(), id="hotfix-branch"),
    ],
)
def test_continuous_deployment_release_resolver(
    branch_name: str,
    latest_version: str,
    current_version: str,
    expected: Union[Optional[str], VersionResolutionError],
):
    provider = DummyVersionProvider.from_string(current_version, latest_version)
    with patch(
        "scripts.release.version._version._resolvers.ContinuousDeploymentVersionResolver.get_branch_name",
        return_value=branch_name
    ):
        repo = Mock(head=Mock(commit=Mock(hexsha="0")))

        if isinstance(expected, VersionResolutionError):
            with pytest.raises(VersionResolutionError):
                resolver = ContinuousDeploymentVersionResolver(provider, repo)
                resolver.resolve_version()
        else:
            expected_version = Version.parse(expected) if expected else None
            resolver = ContinuousDeploymentVersionResolver(provider, repo)
            assert resolver.resolve_version() == expected_version
