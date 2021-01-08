from logging import getLogger
from typing import Optional

from git import Repo
from semver import Version

from .._config import VERSION_TAG_COMMIT_MESSAGE_FORMAT
from .._tags import to_tag

__all__ = ["tag_version"]

logger = getLogger(__name__)


def tag_version(repo: Repo, version: Version, *, push_tag: bool = False, force_tag: bool = False) -> None:

    tag = to_tag(version)

    if tag in repo.tags:
        if repo.tags[tag].commit == repo.head.commit:
            logger.info("The version: %s is already tagged on the commit: %s", version.text, repo.head.commit.hexsha)
            return
        if not force_tag:
            raise ValueError(
                "The version: %s is has already been tagged on another commit: %s. "
                "I cannot apply it to the current commit.",
                version.text,
            )

    commit_message = VERSION_TAG_COMMIT_MESSAGE_FORMAT.format(commit_sha=repo.head.commit.hexsha, version=version.text)
    new_tag = repo.create_tag(tag, message=commit_message, force_tag=force_tag)

    if push_tag:
        repo.remotes.origin.push(new_tag)
