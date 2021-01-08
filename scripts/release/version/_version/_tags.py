"""
Management of tag based version.
"""
import re
from typing import Callable, Collection, Optional

from git import Repo, Tag
from semver import Version

from ._config import VERSION_TAG_STRING_FORMAT
from ._stages import VERSION_PATTERN

__all__ = ["from_tag", "to_tag", "get_versions"]

VERSION_TAG_PATTERN_STRING = f"(?P<version>{VERSION_PATTERN.pattern.lstrip('^').rstrip('$')})"
VERSION_TAG_PATTERN_STRING = VERSION_TAG_STRING_FORMAT.format(version=VERSION_TAG_PATTERN_STRING)
VERSION_TAG_PATTERN = re.compile(f"^({VERSION_TAG_PATTERN_STRING})$")


def from_tag(tag: str) -> Optional[Version]:
    match = VERSION_TAG_PATTERN.match(tag)
    if match:
        return Version.parse(match.group("version"))
    return None


def to_tag(version: Optional[Version]) -> Optional[str]:
    return VERSION_TAG_STRING_FORMAT.format(version=version.text) if version else None


def get_versions(repo: Repo, predicate: Optional[Callable[[Tag, Version], bool]] = None) -> Collection[Version]:
    versions = []
    for tag in repo.tags:
        version = from_tag(tag.name)
        if version and (predicate is None or predicate(tag, version)):
            versions.append(version)
    return versions
