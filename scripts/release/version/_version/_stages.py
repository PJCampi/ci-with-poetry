from enum import Enum
from functools import total_ordering
import re
from typing import Any

from semver import Version

from ._config import HASH_SIZE

__all__ = ["get_stage", "is_valid_version", "Stage", "to_next_stage", "VERSION_PATTERN"]


@total_ordering
class Stage(Enum):
    ALPHA = "alpha"
    RELEASE_CANDIDATE = "rc"
    RELEASE = "release"
    POST = "post"

    def __hash__(self) -> int:
        return self.__index__()

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return False
        return self.__index__() == other.__index__()

    def __lt__(self, other: "Stage") -> bool:
        return self.__index__().__lt__(other.__index__())

    def __ge__(self, other: "Stage") -> bool:
        return self.__index__().__ge__(other.__index__())

    def __index__(self) -> int:
        return next(i for i, val in enumerate(type(self).__members__) if self.name == val)


VERSION_PATTERN = re.compile(
    r"^(\d\.\d\.\d((-{alpha}|((-{rc}|\+{post})\d))(\+[a-z0-9]{{{hash_size}}})?)?)$".format(
        alpha=Stage.ALPHA.value, rc=Stage.RELEASE_CANDIDATE.value, post=Stage.POST.value, hash_size=HASH_SIZE
    )
)


def is_valid_version(version: Version) -> bool:
    return VERSION_PATTERN.match(version.text) is not None


def get_stage(version: Version) -> Stage:
    for stage in Stage.__members__.values():
        if stage.value in version.text:
            return stage
    if version == version.stable and not version.build:
        return Stage.RELEASE
    raise NotImplementedError(f"I could not resolve the stage of version: {version}.")


def to_next_stage(version: Version, stage: Stage, commit_sha: str) -> Version:

    current_stage = get_stage(version)

    if stage is Stage.ALPHA:
        if current_stage > Stage.ALPHA:
            version = version.stable.next_minor
        return Version(version.major, version.minor, version.patch, pre=Stage.ALPHA.value, build=commit_sha[:HASH_SIZE])

    if stage is Stage.RELEASE_CANDIDATE:
        n = int(version.prerelease[1]) + 1 if current_stage is Stage.RELEASE_CANDIDATE else 1
        if current_stage > Stage.RELEASE_CANDIDATE:
            version = version.stable.next_minor
        return Version(version.major, version.minor, version.patch, pre=f"{Stage.RELEASE_CANDIDATE.value}{n}")

    if stage is Stage.POST:
        n = int(version.build[0]) + 1 if current_stage is Stage.POST else 1
        return Version(version.major, version.minor, version.patch, build=f"{Stage.POST.value}{n}")

    if stage is Stage.RELEASE:
        return version.next_patch

    raise NotImplementedError(f"to_next_stage is not implemented for stage: {stage.name}.")
