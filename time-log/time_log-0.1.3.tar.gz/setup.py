# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['time_log']
install_requires = \
['pretty-tables>=1.3.0,<2.0.0', 'yacf>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['tl = time_log:main']}

setup_kwargs = {
    'name': 'time-log',
    'version': '0.1.3',
    'description': 'Prototype for a time tracker/logger command line utility',
    'long_description': '# tl Prototype\n\nPrototype of a time tracker/logger command line utility\n\n\n',
    'author': 'Max Resing',
    'author_email': 'max.resing@protonmail.com',
    'maintainer': 'Max Resing',
    'maintainer_email': 'max.resing@protonmail.com',
    'url': 'https://github.com/resingm/tl-prototype',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
