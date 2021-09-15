import os
from datetime import datetime
from time import sleep

from divinegift.config import Settings
from divinegift.logger import Logger
from divinegift.main import get_args, get_log_param
from typing import List, Dict


class Application:
    def __init__(self):
        self.st = datetime.now()
        self.sp = datetime.now()
        self.args = get_args()
        self.lp = get_log_param(self.args)
        self.logger = Logger()
        self.logger.set_log_level(**self.lp)

        self.settings = Settings(logger_=self.logger)
        self.settings_edited_at = None
        self.conf_file_path = self.args.get('c', 'settings.ini')
        self.cipher_key_path = self.args.get('ck', 'key.ck')

        self.print_intro()

        self.logger.log_info(f'{"=" * 20} START {"=" * 20}')

    def __repr__(self):
        return f'Application()'

    def run(self):
        settings_edited_at = os.path.getmtime(self.conf_file_path)
        if settings_edited_at != self.settings_edited_at:
            self.set_settings()

    def run_service(self):
        while True:
            self.run()
            sleep(self.get_settings('service_wait', 5))

    def set_settings(self):
        self.settings.parse_settings(self.conf_file_path, self.cipher_key_path, ignore_parse_cnt=True)
        self.settings_edited_at = os.path.getmtime(self.conf_file_path)

        self.init_config()

    def init_config(self):
        if not os.path.exists('key.ck'):
            self.settings.initialize_cipher()
            self.encrypt_password('email_conf', 'pwd')
            self.settings.save_settings(self.conf_file_path)

    def encrypt_password(self, connection_name: str, pass_field: str = 'db_pass'):
        try:
            self.settings.encrypt_password(connection_name, pass_field)  # Change it for your config
        except Exception as ex:
            self.logger.log_err(f'Could not encrypt password: {ex}')

    def get_settings(self, param=None, default=None):
        return self.settings.get_settings(param, default)

    def print_intro(self):
        print(f'Process {self.args.get("name")} started!')
        log_place = os.path.join(self.lp.get("log_dir"), self.lp.get("log_name")) if self.lp.get(
            "log_name") else "ON SCREEN"
        print(f'Log will be here: {log_place}')

    def log_debug(self, *args, separator: str = ' '):
        self.logger.log_debug(*args, separator)

    def log_info(self, *args, separator: str = ' '):
        self.logger.log_info(*args, separator)

    def log_warning(self, *args, separator: str = ' '):
        self.logger.log_warn(*args, separator)

    def log_warn(self, *args, separator: str = ' '):
        self.logger.log_warn(*args, separator)

    def log_err(self, *args, separator: str = ' ', src: str = None, mode: List = None, channel: Dict = None):
        self.logger.log_err(*args, separator, src, mode, channel)

    def log_crit(self, *args, separator: str = ' '):
        self.logger.log_crit(*args, separator)
