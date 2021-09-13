from omniblack.repo import Package
from .semver import SemVersion
from dataclasses import dataclass, field


@dataclass
class VersionedPackage(Package):
    version: SemVersion = field(init=False)

    def __post_init__(self):
        if self.python is None or self.javascript is None:
            return

        py_ver = SemVersion.parse(self.python.tool.poetry.version)
        js_ver = SemVersion.parse(self.javascript.version)

        if py_ver != js_ver:
            raise ValueError(f'{self.config.name} has mismatched versions')

        self.version = py_ver
