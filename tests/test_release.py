from importlib import import_module
from pathlib import Path

from toml import load

PROJECT_PATH = Path(__file__).parent.parent
PACKAGE_NAME = load(PROJECT_PATH / "pyproject.toml")["tool"]["poetry"]["name"]


def test_version_is_stamped_in_init_file():
    init_path = PROJECT_PATH / PACKAGE_NAME / "__init__.py"
    assert (
        "__version__" in init_path.read_text()
    ), "The release framework expects the version file to be in the package's __init__ file."

    package_module = import_module(PACKAGE_NAME)
    assert (
        getattr(package_module, "__version__", "") == "0.0.0"
    ), "The release framework expects versions to be stamped by tags, not explicitly in the package. Please roll back!"
