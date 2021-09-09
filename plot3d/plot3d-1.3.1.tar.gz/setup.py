# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plot3d', 'plot3d.paraview']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses_json',
 'diversipy',
 'doepy',
 'matplotlib>=3.3.1,<4.0.0',
 'numpy',
 'pandas',
 'psutil',
 'pydoe',
 'tqdm']

setup_kwargs = {
    'name': 'plot3d',
    'version': '1.3.1',
    'description': 'Plot3D python utilities for reading and writing and also finding connectivity between blocks',
    'long_description': None,
    'author': 'Paht Juangphanich',
    'author_email': 'paht.juangphanich@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.9,<4.0.0',
}


setup(**setup_kwargs)
