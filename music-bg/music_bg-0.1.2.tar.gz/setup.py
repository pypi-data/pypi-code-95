# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['music_bg', 'music_bg.dbus', 'music_bg.img_processors']

package_data = \
{'': ['*']}

install_requires = \
['Pillow-SIMD>=7.0.0,<8.0.0',
 'PyGObject>=3.40.1,<4.0.0',
 'dbus-python>=1.2.16,<2.0.0',
 'entrypoints>=0.3,<0.4',
 'loguru>=0.5.3,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['music_bg = music_bg.__main__:main'],
 'mbg_processors': ['fit = music_bg.img_processors.fit:fit',
                    'noop = music_bg.img_processors.noop:noop',
                    'resize = music_bg.img_processors.resize:resize']}

setup_kwargs = {
    'name': 'music-bg',
    'version': '0.1.2',
    'description': 'Dynamic wallpapers with power of mpris2.',
    'long_description': None,
    'author': 'Pavel Kirilin',
    'author_email': 'win10@list.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
