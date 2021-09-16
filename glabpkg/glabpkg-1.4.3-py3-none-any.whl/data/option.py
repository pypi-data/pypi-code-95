from pathlib import Path

from glabpkg.version import __version__
from pkglts.option_object import Option


class OptionGlabData(Option):
    def version(self):
        return __version__

    def root_dir(self):
        return Path(__file__).parent

    def require_option(self, cfg):
        return ['glabpkg']
