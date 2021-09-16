import os
import toml
import datetime as dt
import pyhectiqlab.ops as ops

from pathlib import Path

class AuthProvider(object):
    """
    Class used to handle oAuth
    """
    def __init__(self, port=8082):
        self.port = str(port)
        self.profile = os.environ.get('HECTIQLAB_PROFILE') or 'default'
        self._load_local_api_keys()
        return
    
    def profile_exists(self, profile):
        return profile in self.profiles

    def change_profile(self, name):
        if name in self.profiles:
            self.profile = name

    def is_logged(self):
        if self.secret_api_key is not None:
            return True
        return False
    
    def fetch_secret_api_token(self, username:str, password:str):
        res = ops.fetch_secret_api_token(username, password)
        if res.get('status_code')!=200:
            return False, None
        self._update_local_api_keys(username, username, res.get('secret_api_key'), res.get('secret_api_key_uuid'))
        self._load_local_api_keys()
        self.profile = username
        api_key_uuid = res.get('secret_api_key_uuid')
        return True, api_key_uuid

    @property
    def secret_api_key(self):
        if self.profile in self.profiles:
            if 'secret_api_key' in self.profiles[self.profile]:
                return self.profiles[self.profile]["secret_api_key"]
        else:
            return None

    def _load_local_api_keys(self):
        self.profiles = {}
        if os.path.isfile(self.tokens_path):
            with open(self.tokens_path, 'r') as f:
                self.profiles = toml.load(f)
            if len(self.profiles)==1:
                self.profile = list(self.profiles.keys())[0]                
        return

    def _update_local_api_keys(self, profile, username, secret_api_key, secret_api_key_uuid):
        self._load_local_api_keys()
        self.profiles[profile] = {'secret_api_key': secret_api_key, 
                                    'username': username, 
                                    'api_key_uuid': secret_api_key_uuid}
        if not os.path.exists(self.tokens_folder):
            os.mkdir(self.tokens_folder)

        with open(self.tokens_path, 'w') as f:
            toml.dump(self.profiles, f)

    @property
    def tokens_path(self):
        if os.environ.get('HECTIQLAB_CREDENTIALS'):
            return os.environ.get('HECTIQLAB_CREDENTIALS')
        else:
            home = str(Path.home())
            config_folder = os.path.join(home, '.hectiqlab')
            return os.path.join(config_folder, 'credentials')
    
    @property
    def tokens_folder(self):
        home = str(Path.home())
        config_folder = os.path.join(home, '.hectiqlab')
        return config_folder
