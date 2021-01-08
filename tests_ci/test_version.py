import pytest
from semver import Version

from scripts.release.version._version._stages import to_next_stage, Stage


@pytest.mark.parametrize(
    "version, stage, expected",
    [
        pytest.param("0.0.0-alpha+12345678", Stage.ALPHA, "0.0.0-alpha+12345678", id="alpha-alpha"),
        pytest.param("0.0.0-alpha+12345678", Stage.RELEASE_CANDIDATE, "0.0.0-rc1", id="alpha-rc"),
        pytest.param("0.0.0-alpha+12345678", Stage.RELEASE, "0.0.0", id="alpha-release"),
        pytest.param("0.0.0-alpha+12345678", Stage.POST, "0.0.0+post1", id="alpha-post"),
        pytest.param("0.0.0-rc1", Stage.ALPHA, "0.1.0-alpha+12345678", id="rc-alpha"),
        pytest.param("0.0.0-rc1", Stage.RELEASE_CANDIDATE, "0.0.0-rc2", id="rc-rc"),
        pytest.param("0.0.0-rc1", Stage.RELEASE, "0.0.0", id="rc-release"),
        pytest.param("0.0.0-rc1", Stage.POST, "0.0.0+post1", id="rc-post"),
        pytest.param("0.0.0", Stage.ALPHA, "0.1.0-alpha+12345678", id="release-alpha"),
        pytest.param("0.0.0", Stage.RELEASE_CANDIDATE, "0.1.0-rc1", id="release-rc"),
        pytest.param("0.0.0", Stage.RELEASE, "0.0.1", id="release-release"),
        pytest.param("0.0.0", Stage.POST, "0.0.0+post1", id="release-post"),
        pytest.param("0.0.0+post1", Stage.ALPHA, "0.1.0-alpha+12345678", id="post-alpha"),
        pytest.param("0.0.0+post1", Stage.RELEASE_CANDIDATE, "0.1.0-rc1", id="post-rc"),
        pytest.param("0.0.0+post1", Stage.RELEASE, "0.0.1", id="post-release"),
        pytest.param("0.0.0+post1", Stage.POST, "0.0.0+post2", id="post-post"),

    ],
)
def test_to_next_stage(version: str, stage: Stage, expected: str):
    assert to_next_stage(Version.parse(version), stage, "12345678") == Version.parse(expected)
