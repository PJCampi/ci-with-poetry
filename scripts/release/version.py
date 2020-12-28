from argparse import ArgumentParser
from contextlib import suppress
import re
from typing import Iterable, Optional

from semver import Version
from semver.exceptions import ParseVersionError

__all__ = ["infer_version", "get_latest_version_tag"]

VERSION_PATTERN, HASH_PATTERN = "{stable}-{pre_post}{n}{build_hash}", "+{short_hash}"
DEVELOP_BRANCH, ALPHA = "develop", "alpha"
RELEASE_BRANCH, RELEASE_CANDIDATE = "release", "rc"
RELEASE_BRANCH_PATTERN = re.compile(f"{RELEASE_BRANCH}/v(?P<version>[0-9]+.[0-9]+)$")
MASTER_BRANCH = "master"
HOTFIX_BRANCH, POST = "hotfix", "post"


# region public API
def infer_version(
    branch_name: str, commit_hash: str, highest_version_tag: str, commit_version_tag: str
) -> Optional[Version]:
    """
    returns the version of a branch.
    """

    latest_version_tag_is_tagging_commit = commit_version_tag == highest_version_tag

    # get the latest version accessible by the commit
    try:
        latest_version = Version.parse(highest_version_tag) if highest_version_tag else Version(0, 0, 0)
    except ParseVersionError:
        raise ParseVersionError(
            f"The latest version tag from git is not a valid semantic version: {highest_version_tag}."
        )

    # if the branch is a release branch, the version follows the pattern: v{major}.{minor}.0-rc.{N}
    if branch_name.startswith(RELEASE_BRANCH):
        version_match = RELEASE_BRANCH_PATTERN.match(branch_name)
        if version_match is None:
            raise ParseVersionError(
                f"Invalid {RELEASE_BRANCH} branch name: {branch_name}. Valid format: {RELEASE_BRANCH_PATTERN.pattern}."
            )
        branch_version = Version.parse(f"{version_match.group('version')}.0")

        if latest_version.is_prerelease() or latest_version == Version(0, 0, 0):

            if branch_version == latest_version.stable:
                if _is_release_candidate(latest_version):
                    pre_release_nbr = int(latest_version.prerelease[1]) + int(not latest_version_tag_is_tagging_commit)
                elif _is_alpha_pre_release(latest_version):
                    pre_release_nbr = 1
                else:
                    raise ParseVersionError(
                        f"Only release candidates are allowed on the {RELEASE_BRANCH} branch. {latest_version} is not."
                    )
                version_str = VERSION_PATTERN.format(
                    stable=branch_version, pre_post=RELEASE_CANDIDATE, n=pre_release_nbr, build_hash=""
                )
                return Version.parse(version_str)

            if branch_version in {
                latest_version.stable.next_major,
                latest_version.stable.next_minor,
            } and _is_release_candidate(latest_version):
                version_str = VERSION_PATTERN.format(
                    stable=branch_version, pre_post=RELEASE_CANDIDATE, n=1, build_hash=""
                )
                return Version.parse(version_str)

            raise ParseVersionError(
                f"Branch version {branch_version} is not a stable version above the current one: {latest_version}."
            )

        raise ParseVersionError(
            f"The current version is not a pre-release one: {latest_version}. A {RELEASE_BRANCH} branch can only be "
            f"created from a commit in the {DEVELOP_BRANCH} branch."
        )

    # if the branch is the master branch, the version follows the pattern: v{major}.{minor}.{patch}
    if branch_name == MASTER_BRANCH:
        if latest_version.is_prerelease() and not _is_release_candidate(latest_version):
            raise ParseVersionError(
                f"Only {RELEASE_BRANCH} branches (producing versions with the {RELEASE_CANDIDATE} flag) can be merged "
                f"to master. The current version does not seem to originate from a {RELEASE_BRANCH} "
                f"branch: {latest_version}."
            )
        if _is_post_version(latest_version):
            return latest_version.next_patch
        if _is_stable_version(latest_version) and latest_version_tag_is_tagging_commit:
            return latest_version
        return latest_version.next_patch

    if branch_name == DEVELOP_BRANCH:
        if not (latest_version.is_prerelease() or latest_version == Version(0, 0, 0)):
            raise ParseVersionError(
                f"Only pre-release branches should be tagged to the develop branch. "
                f"Version: {latest_version} is not consistent with that."
            )

        if highest_version_tag and latest_version_tag_is_tagging_commit:
            return latest_version

        if latest_version == Version(0, 0, 0) or _is_release_candidate(latest_version):
            base_version = latest_version.stable.next_minor
        elif _is_alpha_pre_release(latest_version):
            base_version = latest_version.stable
        else:
            raise ParseVersionError(
                f"Unknown pre-release part of version: {latest_version}. "
                f"Only '{RELEASE_CANDIDATE}' and '{ALPHA}' are allowed."
            )

        version_str = VERSION_PATTERN.format(
            stable=base_version, pre_post=ALPHA, n="", build_hash=HASH_PATTERN.format(short_hash=commit_hash)
        )
        return Version.parse(version_str)

    if branch_name == HOTFIX_BRANCH:
        if _is_post_version(latest_version):
            if latest_version_tag_is_tagging_commit:
                return latest_version
            build = int(latest_version.build[0])
            stable_version = Version(latest_version.major, latest_version.minor, latest_version.patch)
            version_str = VERSION_PATTERN.format(stable=stable_version, pre_post=POST, n=build + 1, build_hash="")
        elif _is_stable_version(latest_version):
            version_str = VERSION_PATTERN.format(stable=latest_version, pre_post=POST, n=1, build_hash="")
        else:
            raise ParseVersionError(
                f"{HOTFIX_BRANCH.title()} can only be created from the {MASTER_BRANCH} branch. "
                f"Version: {latest_version} is not consistent with that."
            )
        return Version.parse(version_str)

    try:
        return Version.parse(commit_version_tag)
    except ParseVersionError:
        return None


def get_latest_version(tags: Iterable[str]) -> Optional[Version]:
    max_version: Optional[Version] = None
    for tag in tags:
        with suppress(ParseVersionError):
            version = Version.parse(tag)
            if max_version:
                if version >= max_version:
                    max_version = version
            else:
                max_version = version
    return max_version


# endregion

# region CLI
def _format_version(version: Optional[Version]) -> str:
    return f"v{version.text}" if version else ""


def _parse_version_tag(version_tag: str) -> str:
    return version_tag.lstrip("v") if version_tag else version_tag


cli_parser = ArgumentParser(usage="Utility tools for versioning application. Versions follow semantic versioning.")
subparsers = cli_parser.add_subparsers()

infer_parser = subparsers.add_parser("infer", usage="Infers the version of the package.")
infer_parser.add_argument("branch_name", help="The name of the branch of the current commit.")
infer_parser.add_argument("commit_hash", help="The short hash of the current commit.")
infer_parser.add_argument(
    "highest_version_tag",
    nargs="?",
    help="The highest version tag accessible from the current commit.",
    default="",
    type=_parse_version_tag,
)
infer_parser.add_argument(
    "commit_version_tag",
    nargs="?",
    help="The highest version tag of the current commit if any.",
    default="",
    type=_parse_version_tag,
)
infer_parser.set_defaults(
    func=lambda a: print(
        _format_version(infer_version(a.branch_name, a.commit_hash, a.highest_version_tag, a.commit_version_tag))
    )
)

highest_version_parser = subparsers.add_parser(
    "latest", usage="Returns the highest version tag from a comma delimited list of tags."
)
highest_version_parser.add_argument(
    "tags",
    help="A list of git version tags.",
    nargs="?",
    default=[],
    type=lambda s: list(map(_parse_version_tag, s.split(","))) if s else [],
)
highest_version_parser.set_defaults(func=lambda a: print(_format_version(get_latest_version(a.tags))))


# endregion

# region private methods
def _is_alpha_pre_release(version: Version) -> bool:
    return version.is_prerelease() and version.prerelease[0] == ALPHA


def _is_release_candidate(version: Version) -> bool:
    return version.is_prerelease() and version.prerelease[0] == RELEASE_CANDIDATE


def _is_stable_version(version: Version) -> bool:
    return version.stable == version


def _is_post_version(version: Version) -> bool:
    return POST in version.text


# endregion

if __name__ == "__main__":
    args = cli_parser.parse_args()
    args.func(args)
