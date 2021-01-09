from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest
from git import Repo
from poetry.core.semver import Version

from scripts.release.version._version._providers import VersionProviderFromTags
from scripts.release.version._version._stages import Stage


@pytest.mark.parametrize(
    "versions, stage, expected",
    [
        pytest.param([], None, None, id="no-version"),
        pytest.param([], Stage.ALPHA, None, id="no-version-stage"),
        pytest.param(["0.0.0", "0.1.0-rc1", "0.1.0"], None, "0.1.0", id="highest-of-all"),
        pytest.param(["0.0.0", "0.1.0-rc1", "0.1.0"], Stage.RELEASE_CANDIDATE, "0.1.0-rc1", id="highest-rc"),
        pytest.param(["0.0.0", "0.1.0-rc1", "0.1.0"], Stage.ALPHA, None, id="highest-alpha"),
    ],
)
def test_simple_version_provider(versions: List[Version], stage: Stage, expected: Optional[Version]):
    with patch(
            "scripts.release.version._version._providers.get_versions",
            return_value=list(map(Version.parse, versions))
    ):
        resolver = VersionProviderFromTags(MagicMock(spec=Repo))
        resolved = resolver.get_latest_version(stage)
        assert (resolved.text if resolved else resolved) == expected
