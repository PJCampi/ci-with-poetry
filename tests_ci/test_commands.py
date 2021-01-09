from unittest.mock import patch
from pathlib import Path

from git import Repo
from poetry.core.semver import Version
import pytest

from scripts.release.version._version._commands import get_version, tag_version
from scripts.release.version._version._commands._add import _add_version_to_package_version_file


@patch("scripts.release.version._version._commands._get.CONTINUOUS_DEPLOYMENT", return_value=True)
def test_continuous_delivery(_, git_repo):

    # initial commit to master
    _add_change(git_repo, "initial commit")
    master = git_repo.api.refs[0]
    _infer_version_and_add(git_repo.api, Version(0, 0, 0))

    # add a development commit
    develop = git_repo.api.create_head("develop")
    develop.checkout()
    _add_change(git_repo, "some development")
    _infer_version_and_add(git_repo.api, Version(0, 1, 0, pre="alpha", build=git_repo.api.head.commit.hexsha[:8]))

    # merge to master
    master.checkout()
    git_repo.api.git.merge(develop)
    _infer_version_and_add(git_repo.api, Version(0, 1, 0))

    # add another a development commit not inferred
    develop.checkout()
    _add_change(git_repo, "some more development")

    # merge to master
    master.checkout()
    git_repo.api.git.merge(develop)
    _infer_version_and_add(git_repo.api, Version(0, 2, 0))


def test_git_flow(git_repo):

    # initial commit to master
    _add_change(git_repo, "initial commit")
    master = git_repo.api.refs[0]
    _infer_version_and_add(git_repo.api, Version(0, 0, 0))

    # add a development commit
    develop = git_repo.api.create_head("develop")
    develop.checkout()
    _add_change(git_repo, "some development")
    _infer_version_and_add(git_repo.api, Version(0, 1, 0, pre="alpha", build=git_repo.api.head.commit.hexsha[:8]))

    # add another development commit
    _add_change(git_repo, "another development")

    # create a release candidate branch
    release_1 = git_repo.api.create_head("release/v0.1")
    release_1.checkout()
    _infer_version_and_add(git_repo.api, Version(0, 1, 0, pre="rc1"))

    # another release candidate
    _add_change(git_repo, "a change to the release candidate")
    _infer_version_and_add(git_repo.api, Version(0, 1, 0, pre="rc2"))

    # make a patch on master
    master.checkout()
    _add_change(git_repo, "a patch")
    _infer_version_and_add(git_repo.api, Version(0, 0, 1))

    # another change on develop
    develop.checkout()
    _add_change(git_repo, "some more development")
    _infer_version_and_add(git_repo.api, Version(0, 2, 0, pre="alpha", build=git_repo.api.head.commit.hexsha[:8]))

    # release v1
    master.checkout()
    git_repo.api.git.merge(release_1)
    git_repo.api.delete_head(release_1)
    _infer_version_and_add(git_repo.api, Version(0, 1, 0))

    # create a hotfix branch and add changes to it
    hotfix = git_repo.api.create_head("hotfix/something-did-not-work")
    hotfix.checkout()
    _add_change(git_repo, "something did not work")
    _add_change(git_repo, "something else did not work")
    _infer_version_and_add(git_repo.api, Version(0, 1, 0,  build=f"post1"))

    # merge hotfix branch to master
    master.checkout()
    git_repo.api.git.merge(hotfix)
    git_repo.api.delete_head(hotfix)
    _infer_version_and_add(git_repo.api, Version(0, 1, 1))


def _add_change(git_repo, a_change: str) -> None:

    # add changes to our file
    file = git_repo.workspace / 'committed.txt'
    file_text = file.read_text() if file.exists() else ""
    file.write_text(f"{file_text}\n{a_change}" if file_text else a_change)

    # commit the change
    git_repo.api.git.add(update=True)
    git_repo.api.index.commit(f"committing: {a_change}")


def _infer_version_and_add(repo: Repo, expected_version: Version) -> None:
    version = get_version(repo, infer=True, include_alpha=True)
    assert version == expected_version
    tag_version(repo, version)
    assert f"v{expected_version.text}" in repo.tags


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
