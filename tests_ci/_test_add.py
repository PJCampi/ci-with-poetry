from pathlib import Path

from semver import Version
import pytest

from scripts.release.version._version._commands._add import _add_version_to_package_version_file


@pytest.mark.parametrize(
    "file_name, n_replaced, n_not_replaced",
    [
        pytest.param("only_version.py", 1, 0, id="only-version"),
        pytest.param("version_comments_etc.py", 1, 3, id="version-comments")
    ]
)
def test_add_package(file_name, n_replaced, n_not_replaced, tmp_path):
    file_path = Path(__file__).parent / "version_files" / file_name
    version = Version(1, 0, 0)
    new_path = tmp_path / file_name
    new_path.write_text(file_path.read_text())
    _add_version_to_package_version_file(new_path, version)
    with_version = new_path.read_text()
    assert with_version.count("0.0.0") == 0
    assert with_version.count("1.0.0") == n_replaced
    assert with_version.count("1.1.1") == n_not_replaced
