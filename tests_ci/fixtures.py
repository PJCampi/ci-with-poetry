from types import MappingProxyType
from typing import Mapping, Optional

from semver import Version

from scripts.release.version._version._stages import Stage
from scripts.release.version._version._providers import IVersionProvider

__all__ = ["DummyVersionProvider"]


class DummyVersionProvider(IVersionProvider):

    def __init__(
            self,
            current_version: Optional[Version] = None,
            latest_version: Optional[Version] = None,
            latest_versions: Mapping[Stage, Version] = MappingProxyType({}),
    ):
        self._current_version = current_version
        self._latest_version = latest_version
        self._latest_versions = latest_versions

    @classmethod
    def from_string(cls, current_version: str = "", latest_version: str = ""):
        return DummyVersionProvider(
            Version.parse(current_version) if current_version else None,
            Version.parse(latest_version) if latest_version else None
        )

    def get_current_version(self) -> Optional[Version]:
        return self._current_version

    def get_latest_version(self, in_stage: Optional[Stage] = None) -> Optional[Version]:
        if in_stage:
            return self._latest_versions.get(in_stage, default=None)
        return self._latest_version
