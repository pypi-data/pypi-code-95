# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['checkmark']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'checkmark',
    'version': '0.0.0',
    'description': 'Write HTML forms in a Markdown-like language',
    'long_description': '# Checkmark\n\nWrite HTML forms in a Markdown-like language.',
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/deepadmax/checkmark',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
