from argparse import ArgumentParser
from contextlib import suppress
from typing import Iterable, Optional

from semver import Version
from semver.exceptions import ParseVersionError

from infer_version_tag import format_version_tag, parse_version_tag

__all__ = ["get_latest_version_tag"]


def get_latest_version_tag(tags: Iterable[str]) -> str:
    max_version: Optional[Version] = None
    for tag in tags:
        with suppress(ParseVersionError):
            version = Version.parse(tag)
            if max_version:
                if version >= max_version:
                    max_version = version
            else:
                max_version = version
    return str(max_version or "")


argument_parser = ArgumentParser(
    "Returns the highest version tag from a comma delimited list of tags. "
    "We follow semver semantic. Invalid versions are excluded."
)
argument_parser.add_argument(
    "tags", help="A list of git version tags.", nargs="?", default=[], type=lambda s: s.split(",") if s else []
)


if __name__ == "__main__":
    args = argument_parser.parse_args()
    latest_version = get_latest_version_tag(map(parse_version_tag, args.tags))
    print(format_version_tag(latest_version))
