import pytest
from poetry.core.semver import Version

from scripts.release.version._version._tags import from_tag, to_tag


@pytest.mark.parametrize(
    "tag, expected",
    [
        pytest.param("v0.0.0", Version(0, 0, 0), id="stable"),
        pytest.param("v0.1.0-rc1", Version(0, 1, 0), id="release-candidate"),
        pytest.param("v0.1.0-rc", None, id="wrong-release-candidate-1"),
        pytest.param("v0.1.0rc1", None, id="wrong-release-candidate-2"),
        pytest.param("v0.1.0+post", None, id="wrong-post"),
        pytest.param("v0.1.0+post+12345678", None, id="wrong-post-with-commit"),
        pytest.param("v0.1.0+post1", Version(0, 1, 0), id="post"),
        pytest.param("v0.1.0+post1+12345678", Version(0, 1, 0), id="post-with-commit"),
        pytest.param("v0.1.0-alpha+12345678", Version(0, 1, 0), id="alpha"),
        pytest.param("v0.1.0-alpha1+12345678", None, id="wrong-alpha"),
        pytest.param("v0.1.0+12345678", None, id=" no-stage"),
        pytest.param("v0.1.0-x+12345678", None, id=" wrong-stage"),
    ],
)
def test_version(tag: str, expected: Version):
    version = from_tag(tag)
    assert (Version(version.major, version.minor, version.patch) if version else version) == expected
    if version:
        assert to_tag(version) == tag
