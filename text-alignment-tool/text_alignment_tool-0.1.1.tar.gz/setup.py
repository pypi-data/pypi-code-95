# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['text_alignment_tool',
 'text_alignment_tool.alignment_algorithms',
 'text_alignment_tool.alignment_tool',
 'text_alignment_tool.find_wordlist_for_alignment',
 'text_alignment_tool.shared_classes',
 'text_alignment_tool.text_loaders',
 'text_alignment_tool.text_transformers']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'text-alignment-tool',
    'version': '0.1.1',
    'description': 'A tool for performing complex text alignment processes.',
    'long_description': None,
    'author': 'Bronson Brown-deVost',
    'author_email': 'bronsonbdevost@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
