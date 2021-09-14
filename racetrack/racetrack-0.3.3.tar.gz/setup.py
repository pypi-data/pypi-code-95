# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['racetrack', 'racetrack.tracks']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'colorama>=0.4.4,<0.5.0', 'momba[all]>=0.3.10,<0.4.0']

entry_points = \
{'console_scripts': ['racetrack = racetrack.__main__:main']}

setup_kwargs = {
    'name': 'racetrack',
    'version': '0.3.3',
    'description': 'A formal model of the Racetrack benchmark.',
    'long_description': '# Racetrack',
    'author': 'Maximilian Köhl',
    'author_email': 'koehl@cs.uni-saarland.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/koehlma/momba',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
