import os
import json


_WINDOWS_PATH = r'i:/config.json'
_LINUX_PATH = r'/root/projects/config.json'

class ConfigError(Exception): pass

# Определяем расположение конфиг файла
if os.name == 'nt':
    _conf_path = _WINDOWS_PATH
elif os.name == 'posix':
    _conf_path = _LINUX_PATH
else:
    raise ConfigError(f'Unknown OS: {os.name}')

# Загружаем файл конфига
with open(_conf_path) as f:
    _conf_data = json.loads(f.read())

# Генерируем оболочку
class _config:
    class webdav:
        _clsname = _conf_data['webdav']
        hostname: str       = _clsname['hostname']
        login: str          = _clsname['login']
        password: str       = _clsname['password']
        timeout: int        = _clsname['timeout']
        disable_check: int  = _clsname['disable_check']
        verbose: int        = _clsname['verbose']

    class rabbitmq:
        _clsname        = _conf_data['rabbitmq']
        login: str      = _clsname['login']
        password: str   = _clsname['password']
        hostname: str   = _clsname['hostname']
        port: int       = _clsname['port']
        port_web: int   = _clsname['port_web']

    class pypi:
        _clsname        = _conf_data['pypi']
        login: str      = _clsname['login']
        password: str   = _clsname['password']

config = _config()

if __name__ == '__main__':
    print(config.rabbitmq.login)
    print(config.webdav.login)
