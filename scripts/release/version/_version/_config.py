from pathlib import Path

__all__ = [
    "CONTINUOUS_DEPLOYMENT",
    "DEVELOP",
    "DETACHED_HEAD",
    "FEATURE",
    "HASH_SIZE",
    "HOTFIX",
    "MASTER",
    "PROJECT_DIR",
    "RELEASE",
    "VERSION_FILE_NAME",
    "VERSION_TAG_STRING_FORMAT",
    "VERSION_TAG_COMMIT_MESSAGE_FORMAT",
]

CONTINUOUS_DEPLOYMENT = False
FEATURE, DEVELOP, RELEASE, MASTER, HOTFIX, DETACHED_HEAD = "feature", "develop", "release", "master", "hotfix", "head"
HASH_SIZE = 8
PROJECT_DIR = Path(__file__).parent.parent.parent.parent.parent
VERSION_FILE_NAME = "__init__.py"
VERSION_TAG_STRING_FORMAT = "v{version}"
VERSION_TAG_COMMIT_MESSAGE_FORMAT = "tagging commit: {commit_sha} with version: {version}"
