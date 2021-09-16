# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyriksprot',
 'pyriksprot.dehyphenation',
 'pyriksprot.foss',
 'pyriksprot.resources',
 'pyriksprot.resources.templates']

package_data = \
{'': ['*'], 'pyriksprot.resources': ['xslt/*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'click>=7.1.2,<8.0.0',
 'dehyphen>=0.3.4,<0.4.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.2.3,<2.0.0']

entry_points = \
{'console_scripts': ['parla_frequencies = scripts.parla_frequencies:main',
                     'parla_transform = scripts.parla_transform:main']}

setup_kwargs = {
    'name': 'pyriksprot',
    'version': '2021.9.6',
    'description': 'Python API for Riksdagens Protokoll',
    'long_description': '# Python package for reading and tagging Riksdagens Protokoll\n\nBatteries (tagger) not included.\n\n',
    'author': 'Roger Mähler',
    'author_email': 'roger.mahler@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://westac.se',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
