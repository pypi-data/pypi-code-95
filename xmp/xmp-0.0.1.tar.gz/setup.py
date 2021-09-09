# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xmp']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['xmp = xmp.main:main']}

setup_kwargs = {
    'name': 'xmp',
    'version': '0.0.1',
    'description': 'xmp is execute Python code in Markdown code block.',
    'long_description': None,
    'author': 'hashzmr',
    'author_email': 'rhashizume7729@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hashzmr/xmp',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
