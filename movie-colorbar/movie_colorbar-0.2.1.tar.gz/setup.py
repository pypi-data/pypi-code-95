# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['movie_colorbar']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0', 'loguru>=0.5.0,<0.6.0', 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['colorbar = movie_colorbar.__main__:app']}

setup_kwargs = {
    'name': 'movie-colorbar',
    'version': '0.2.1',
    'description': 'Turn a video into a colorbar',
    'long_description': None,
    'author': 'Felix Soubelet',
    'author_email': 'felix.soubelet@liverpool.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
