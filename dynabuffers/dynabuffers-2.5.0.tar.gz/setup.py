# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynabuffers',
 'dynabuffers.api',
 'dynabuffers.ast',
 'dynabuffers.ast.datatype',
 'dynabuffers.header']

package_data = \
{'': ['*'],
 'dynabuffers': ['antlr/*'],
 'dynabuffers.api': ['map/*'],
 'dynabuffers.ast': ['annotation/*', 'structural/*']}

install_requires = \
['antlr4-python3-runtime==4.7']

entry_points = \
{'console_scripts': ['build = poetry_scripts:build',
                     'clean = poetry_scripts:clean',
                     'install = poetry_scripts:install',
                     'publish = poetry_scripts:publish',
                     'test = poetry_scripts:test']}

setup_kwargs = {
    'name': 'dynabuffers',
    'version': '2.5.0',
    'description': 'Dynamic cross platform serialization library.',
    'long_description': None,
    'author': 'Leftshift One',
    'author_email': 'contact@leftshift.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.5.0,<4.0.0',
}


setup(**setup_kwargs)
