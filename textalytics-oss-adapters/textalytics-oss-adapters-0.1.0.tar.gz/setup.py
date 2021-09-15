# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['textalytics_spacy', 'textalytics_stanza']

package_data = \
{'': ['*']}

install_requires = \
['spacy>=3.1.2,<4.0.0',
 'stanza>=1.2.3,<2.0.0',
 'textalytics-core>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['test = scripts:test']}

setup_kwargs = {
    'name': 'textalytics-oss-adapters',
    'version': '0.1.0',
    'description': 'textalytics interface implementation for popular NLP open source libraries',
    'long_description': None,
    'author': 'Manoj Bharadwaj',
    'author_email': 'manoj@cloudcosmos.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
