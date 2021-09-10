# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['makehash']

package_data = \
{'': ['*']}

install_requires = \
['alive-progress', 'click-anno', 'colorama', 'fsoopify']

entry_points = \
{'console_scripts': ['makehash = '
                     'makehash.entry_points_console_scripts:makehash',
                     'verifyhash = '
                     'makehash.entry_points_console_scripts:verifyhash']}

setup_kwargs = {
    'name': 'makehash',
    'version': '0.1.4',
    'description': 'A CLI tools use to create *.hash file and verify it later.',
    'long_description': '# makehash\n\nA CLI tools use to create *.hash file and verify it later.\n\n## Usage\n\n``` cmd\nmakehash   DIR_OR_FILE      # create *.hash file\nverifyhash DIR_OR_FILE      # verify\n```\n',
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
