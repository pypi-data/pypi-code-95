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
        _x = _conf_data['webdav']
        hostname: str = _x['hostname']
        login: str = _x['login']
        password: str = _x['password']
        timeout: int = _x['timeout']
        disable_check: int = _x['disable_check']
        verbose: int = _x['verbose']

    class rabbitmq:
        _x = _conf_data['rabbitmq']
        login: str = _x['login']
        password: str = _x['password']
        hostname: str = _x['hostname']
        port: int = _x['port']
        port_web: int = _x['port_web']

config = _config()

if __name__ == '__main__':
    print(config.rabbitmq.login)
    print(config.webdav.login)
