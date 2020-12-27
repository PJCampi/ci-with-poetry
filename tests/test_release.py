from importlib import import_module
from pathlib import Path
from typing import Optional, Union

import pytest
from semver import Version
from semver.exceptions import ParseVersionError
from toml import load

from scripts.release.infer_version_tag import infer_version

PROJECT_PATH = Path(__file__).parent.parent
PACKAGE_NAME = load(PROJECT_PATH / "pyproject.toml")["tool"]["poetry"]["name"]


def test_version_is_stamped_in_init_file():
    init_path = PROJECT_PATH / PACKAGE_NAME / "__init__.py"
    assert (
        "__version__" in init_path.read_text()
    ), "The release framework expects the version file to be in the package's __init__ file."

    package_module = import_module(PACKAGE_NAME)
    assert (
        getattr(package_module, "__version__", "") == "0.0.0"
    ), "The release framework expects versions to be stamped by tags, not explicitly in the package. Please roll back!"


@pytest.mark.parametrize(
    "branch_name, commit_hash, latest_version_tag, commit_version_tag, expected",
    [
        pytest.param("develop", "00", "", "", "0.1.0-alpha+00", id="first-commit"),
        pytest.param("develop", "00", "0.1.0-alpha+00", "0.1.0-alpha+00", "0.1.0-alpha+000", id="first-commit-tagged"),
        pytest.param("develop", "00", "0.0.0", "", "0.1.0-alpha+00", id="first-commit-with-initial-version"),
        pytest.param("master", "00", "", "", "0.0.0", id="first-commit-master"),
        pytest.param("master", "00", "0.0.0", "0.0.0", "0.0.0", id="first-commit-master-tagged"),
        pytest.param("master", "00", "0.0.0", "", "0.0.1", id="first-patch"),
        pytest.param("release/v0.0", "00", "0.1.0-alpha+00", "", ParseVersionError(), id="first-release-too-low"),
        pytest.param("release/v0.2", "00", "0.1.0-alpha+00", "", ParseVersionError(), id="first-release-too-high"),
        pytest.param("release/v0.1.1", "00", "0.0.0", "", ParseVersionError(), id="first-release-wrong-format"),
        pytest.param("release/v0.1", "00", "0.1.0-alpha+00", "", "0.1.0-rc1", id="first-release-candidate"),
        pytest.param("release/v0.1", "00", "0.1.0-rc1", "0.1.0-rc1", "0.1.0-rc1", id="first-release-candidate-tagged"),
        pytest.param("develop", "00", "0.1.0-rc1", "0.1.0-rc1", "0.1.0-rc1", id="develop-release-candidate-tagged"),
        pytest.param("release/v0.1", "00", "0.1.0-rc1", "", "0.1.0-rc2", id="first-release-another-candidate"),
        pytest.param("develop", "00", "0.1.0-rc1", "", "0.2.0-alpha+00", id="another-develop-version"),
        pytest.param("develop", "0", "0.2.0-alpha+0", "0.2.0-alpha+0", "0.2.0-alpha+0", id="another-develop-tagged"),
        pytest.param("master", "00", "0.1.0-rc2", "", "0.1.0", id="first-release-successful"),
        pytest.param("master", "00", "0.1.0", "0.1.0", "0.1.0", id="first-release-successful-tagged"),
        pytest.param("master", "00", "0.1.0", "", "0.1.1", id="first-release-patch"),
        pytest.param("master", "00", "0.1.1", "0.1.1", "0.1.1", id="first-release-patch-tagged"),
        pytest.param("master", "00", "0.3.0-rc1", "0.1.1", "0.3.0", id="release-after-botched-one"),
        pytest.param("random-branch", "00", "0.1.0-rc1", "", None, id="random-branch"),
        pytest.param("hotfix", "00", "0.1.0", "0.1.0", "0.1.0-post1", id="hotfix"),
        pytest.param("hotfix", "00", "0.1.0-post1", "0.1.0-post1", "0.1.0-post1", id="hotfix-tagged"),
        pytest.param("hotfix", "00", "0.1.0-post1", "", "0.1.0-post2", id="hotfix-another"),
        pytest.param("master", "00", "0.1.0-post2", "0.1.0-post2", "0.1.1", id="hotfix-merged-to-master"),
    ],
)
def test_versioning(
    branch_name: str,
    commit_hash: str,
    latest_version_tag: str,
    commit_version_tag: str,
    expected: Union[Optional[str], ParseVersionError],
):
    if isinstance(expected, ParseVersionError):
        with pytest.raises(ParseVersionError):
            infer_version(branch_name, commit_hash, latest_version_tag, commit_version_tag)
    else:
        expected_version = Version.parse(expected) if expected else None
        assert infer_version(branch_name, commit_hash, latest_version_tag, commit_version_tag) == expected_version
