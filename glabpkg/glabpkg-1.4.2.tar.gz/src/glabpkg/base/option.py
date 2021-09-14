from pathlib import Path

from glabpkg.version import __version__
from pkglts.option_object import Option


class OptionGlabBase(Option):
    def version(self):
        return __version__

    def root_dir(self):
        return Path(__file__).parent

    def update_parameters(self, cfg):
        cfg['base']['authors'] = [('revesansparole', 'revesansparole@gmail.com')]

        cfg['gitlab']['server'] = "gitlab.com"

        cfg['license']['name'] = 'cc_by_nc'
        cfg['license']['organization'] = 'revesansparole'

        # add a parameter to the option
        cfg[self._name] = dict(docker="revesansparole/glabci")

        return cfg

    def check(self, cfg):
        invalid_params = []

        return invalid_params

    def require_option(self, cfg):
        return ['gitlab', 'reqs', 'doc', 'license']
