

import os
import sys
import shutil
import pkg_resources
from six.moves.configparser import ConfigParser
from appdirs import user_config_dir
from secrets import token_hex


class NetconfigConfig(object):
    _appname = os.path.join('ebs', 'netconfig')
    _root = os.path.abspath(os.path.dirname(__file__))
    _roots = [_root]
    _config_file = os.path.join(user_config_dir(_appname), 'config.ini')

    def __init__(self):
        if not os.path.exists(os.path.dirname(self._config_file)):
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
        if not os.path.exists(self._config_file):
            _ROOT = os.path.abspath(os.path.dirname(__file__))
            shutil.copy(os.path.join(_ROOT, 'default/config.ini'), self._config_file)
        self._config = ConfigParser()
        print("Reading Config File {}".format(self._config_file))
        self._config.read(self._config_file)
        print("EBS Linux Node NetConfig, version {0}".format(self.netconfig_version))

    @property
    def netconfig_version(self):
        return pkg_resources.get_distribution('ebs-linuxnode-netconfig').version

    def _write_config(self):
        with open(self._config_file, 'w') as configfile:
            self._config.write(configfile)

    def _check_section(self, section):
        if not self._config.has_section(section):
            self._config.add_section(section)
            self._write_config()

    @property
    def auth_secret_key(self):
        if not self._config.has_option(section='auth', option='secret_key'):
            self._config.set('auth', 'secret_key', token_hex(32))
            self._write_config()
        return self._config.get('auth', 'secret_key')

    @property
    def auth_username(self):
        return self._config.get('auth', 'username')

    @property
    def auth_password(self):
        return self._config.get('auth', 'password')

    @property
    def wifi_device(self):
        return self._config.get('wifi', 'device')

    @property
    def wpa_supplicant_path(self):
        return self._config.get('wifi', 'wpa_supplicant_path')


_config = NetconfigConfig()
sys.modules[__name__] = _config
