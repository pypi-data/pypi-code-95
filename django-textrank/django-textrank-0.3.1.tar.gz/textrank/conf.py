#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Все следующие настройки должны быть внутри словаря TEXTRANK, когда вы
# определите их в файле settings.py
conf = getattr(settings, 'TEXTRANK', {})

# Пока нет ключей, внешнее API не работает.
API_KEYS = set()
API_KEYS.update(conf.get('API_KEYS', []))
for key in API_KEYS:
    if len(key) < 12:
        raise ImproperlyConfigured(
            'The API_KEYS is not secure: %s' % key)
# Название cookie для проверки ключа API.
API_COOKIE_NAME = conf.get('API_COOKIE_NAME', 'apikey')

# URL-адреса для входа и выхода из системы.
LOGIN_URL = conf.get('LOGIN_URL', 'admin:login')
LOGOUT_URL = conf.get('LOGOUT_URL', 'admin:logout')

# Уровень доступа к системе может быть: 'anonymous', 'user', 'employer',
# или 'superuser'. Заметьте, что в режиме 'anonymous' доступ к API тоже
# будет свободен.
ACCESS_LEVEL = conf.get('ACCESS_LEVEL', 'user')
DEMO_MODE = ACCESS_LEVEL == 'anonymous'

# Форматирование в JSON для API.
JSON_DUMPS_PARAMS = conf.get('JSON_DUMPS_PARAMS',
                             {'indent': 2, 'ensure_ascii': False})
