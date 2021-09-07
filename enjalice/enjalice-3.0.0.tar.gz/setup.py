# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enjalice', 'enjalice.attachments', 'enjalice.request', 'enjalice.response']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

extras_require = \
{'aiohttp': ['aiohttp[speedups]>=3.7.4,<4.0.0']}

setup_kwargs = {
    'name': 'enjalice',
    'version': '3.0.0',
    'description': 'EnjAlice is a asynchronous framework for Yandex Alice API',
    'long_description': '# EnjAlice\n\nEnjAlice - асинхронная обёртка над API Яндекс.Алисы, которая предоставляет возможность быстро запустить и удобно разрабатывать callback диалоги.\n\nДокументация доступна по ссылке: https://enjalice.readthedocs.io/ru/latest/\n\n## Установка\n\n```\npip install enjalice\n```\n\n## Пример бота\n\nВсе примеры находятся в папке /example\n\n## Copyright\nПроект имеет лицензию MIT.\n\nCopyright © Jotty\n',
    'author': 'jotty',
    'author_email': 'bard143games@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jottyVlad/EnjAlice',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
