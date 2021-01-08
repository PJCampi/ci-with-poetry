from argparse import ArgumentParser
from typing import Optional

from git import Repo
from semver import Version

from ._version import add_version_to_project, get_version, tag_version, PROJECT_DIR


def optional(func):
    def wrapped(arg):
        if arg:
            return func(arg)
        return None

    return wrapped


def print_version(version: Optional[Version]) -> None:
    print(version.text if version else "")


cli_parser = ArgumentParser(usage="Utility tools for versioning application. Versions follow semantic versioning.")
subparsers = cli_parser.add_subparsers()

add_version_parser = subparsers.add_parser("add", usage="Adds the version provided to the package.")
add_version_parser.add_argument(
    "version", help="The version to add to the package.", type=Version.parse,
)
add_version_parser.set_defaults(func=lambda r, a: add_version_to_project(a.version))

infer_version_parser = subparsers.add_parser("get", usage="Get the current version of the package.")
infer_version_parser.add_argument(
    "--infer",
    help="Infers the version of the package if the current package is not versioned explicitly.",
    action="store_true",
)
infer_version_parser.add_argument(
    "--include-alpha", help="Include alpha releases", action="store_true",
)
infer_version_parser.set_defaults(
    func=lambda r, a: print_version(get_version(r, infer=a.infer, include_alpha=a.include_alpha))
)

tag_version_parser = subparsers.add_parser("tag", usage="Tags the current commit with the version provided.")
tag_version_parser.add_argument(
    "version", help="The version to add to the package.", type=Version.parse,
)
tag_version_parser.add_argument(
    "--force",
    help="Force the version to be tagged on the current commit even if it already exists. This is not recommended.",
    action="store_true",
)
tag_version_parser.add_argument("--push", help="Push the tag to the remote repository.", action="store_true")
tag_version_parser.set_defaults(func=lambda r, a: tag_version(r, a.version, push_tag=a.push, force_tag=a.force))


if __name__ == "__main__":
    repo = Repo(PROJECT_DIR)
    args = cli_parser.parse_args()
    args.func(repo, args)
