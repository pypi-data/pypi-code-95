# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xcresult']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['xcresult = xcresult:command_line.run']}

setup_kwargs = {
    'name': 'xcresult',
    'version': '13.0.0',
    'description': 'An xcresult parser.',
    'long_description': '# xcresult\n\n',
    'author': 'Dale Myers',
    'author_email': 'dale@myers.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dalemyers/xcresult',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
