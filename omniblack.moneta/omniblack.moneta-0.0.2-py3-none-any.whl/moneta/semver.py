from parver import Version
from attr import attrs, attrib
from itertools import repeat, chain


@attrs(
    slots=True,
    eq=False,
    weakref_slot=True,
    order=False,
    hash=False,
    collect_by_mro=True,
)
class SemVersion(Version):
    major = attrib(init=False)
    minor = attrib(init=False)
    patch = attrib(init=False)

    @major.default
    def _major_default(self):
        try:
            return self.release[0]
        except IndexError:
            return 0

    @minor.default
    def _minor_default(self):
        try:
            return self.release[1]
        except IndexError:
            return 0

    @patch.default
    def _patch_default(self):
        try:
            return self.release[2]
        except IndexError:
            return 0

    def _convert_to_semver(self):
        nums_needed = 3 - len(self.release)
        if nums_needed <= 0:
            return self
        else:
            new_release = tuple(chain(self.release, repeat(0, nums_needed)))
            return self.replace(release=new_release)

    def bump_major(self):
        ver = self._convert_to_semver()
        return ver.bump_release(index=0)

    def bump_minor(self):
        ver = self._convert_to_semver()
        return ver.bump_release(index=1)

    def bump_patch(self):
        ver = self._convert_to_semver()
        return ver.bump_release(index=2)

    def replace(self, **kwargs):
        new_version = super().replace(**kwargs)
        return self.__class__(**new_version._attrs_as_init())
