"""
We separate the logic for retrieving a version (for example via a tag in git, the version in pyproject.toml file
or even in a package repository (f.ex. pypi)) and the process of determining what the next version should be.

The logic for retrieving a version is encapsulated in the VersionProvider class while the logic for determining what
the next version should be is encapsulated in the VersionResolver class.

The tags module provides the low-level implementation of
"""
