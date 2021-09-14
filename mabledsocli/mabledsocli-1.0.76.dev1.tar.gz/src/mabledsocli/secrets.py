import re
from .logger import Logger
from .providers import StoreProvider, Providers
from .stages import Stages
from .constants import *
from .exceptions import *
from .config import ContextSource



REGEX_PATTERN = r"^[a-zA-Z]([.a-zA-Z0-9_-]*[a-zA-ZA-Z0-9])?$"

class SecretProvider(StoreProvider):
    def list(self, config, uninherited=False, decrypt=False, filter=None):
        raise NotImplementedError()
    def add(self, config, key, value):
        raise NotImplementedError()
    def get(self, config, key, decrypt=False, revision=None):
        raise NotImplementedError()
    def history(self, config, key, decrypt=False):
        raise NotImplementedError()
    def delete(self, config, key):
        raise NotImplementedError()


class SecretService():

    def validate_key(self, key):
        Logger.info(f"Validating secret key '{key}'...")
        if not key:
            raise DSOException(MESSAGES['KeyNull'])
        if key == 'dso' or key.startswith('dso.'):
            raise DSOException(MESSAGES['DSOReserverdKey'].format(key))
        if not re.match(REGEX_PATTERN, key):
            raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, REGEX_PATTERN))
        if '..' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '..'))

    def list(self, config, uninherited=False, decrypt=False, filter=None):
        self.config = config
        provider = Providers.SecretProvider()
        Logger.info(f"Start listing secrets: namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)}, application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        return provider.list(config, uninherited, decrypt, filter)

    def add(self, config, key, value):
        self.config = config
        self.validate_key(key)
        provider = Providers.SecretProvider()
        Logger.info(f"Start adding secret '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)}, application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        return provider.add(config, key, value)

    def get(self, config, key, decrypt=False, revision=None):
        # self.validate_key(key)
        self.config = config
        provider = Providers.SecretProvider()
        Logger.info(f"Start getting secret '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)}, application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        return provider.get(config, key, decrypt, revision)

    def history(self, config, key, decrypt=False):
        # self.validate_key(key)
        self.config = config
        provider = Providers.SecretProvider()
        Logger.info(f"Start getting the history of secret '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)}, application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        return provider.history(config, key, decrypt)

    def delete(self, config, key):
        # self.validate_key(key)
        self.config = config
        provider = Providers.SecretProvider()
        Logger.info(f"Start deleting secret '{key}': namespace={config.get_namespace(ContextSource.Target)}, project={config.get_project(ContextSource.Target)}, application={config.get_application(ContextSource.Target)}, stage={config.get_stage(ContextSource.Target, short=True)}, scope={config.scope}")
        return provider.delete(config, key)

Secrets = SecretService()
