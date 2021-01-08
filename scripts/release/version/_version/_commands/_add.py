from logging import getLogger
from pathlib import Path
import re

from poetry.core.toml import TOMLFile
from semver import Version

from .._config import PROJECT_DIR, VERSION_FILE_NAME
from .._stages import VERSION_PATTERN

__all__ = ["add_version_to_project"]

logger = getLogger(__file__)

TOML_FILE_PATH = PROJECT_DIR / "pyproject.toml"

VERSION_PATTERN_STRING = VERSION_PATTERN.pattern.lstrip("^").rstrip("$")
VERSION_PATTERN_STRING_FORMAT = '__version__ = "{pattern}"'
VERSION_PATTERN = re.compile(
    f"(^|\n)({VERSION_PATTERN_STRING_FORMAT.format(pattern=VERSION_PATTERN_STRING)})($|\n)", re.MULTILINE
)


def add_version_to_project(version: Version) -> None:
    """
    Adds the version provided to the pyproject.toml file and the version file.
    """
    # update pyproject.toml
    logger.debug("Adding version: %s to pyproject.toml file", version.text)
    toml_file = TOMLFile(TOML_FILE_PATH)
    content = toml_file.read()
    poetry_content = content["tool"]["poetry"]
    poetry_content["version"] = version.text
    toml_file.write(content)

    # update version file
    package_name = str(poetry_content["name"])
    version_file_path = PROJECT_DIR / package_name.replace("-", "_") / VERSION_FILE_NAME
    logger.debug("Adding version: %s to %s file", version.text, VERSION_FILE_NAME)
    _add_version_to_package_version_file(version_file_path, version)


def _add_version_to_package_version_file(version_file_path: Path, version: Version) -> None:
    version_file_content = version_file_path.read_text()
    content_replaced = VERSION_PATTERN.sub(
        VERSION_PATTERN_STRING_FORMAT.format(pattern=version.text), version_file_content
    )
    version_file_path.write_text(content_replaced)
