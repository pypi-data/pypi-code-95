# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colores']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0']

setup_kwargs = {
    'name': 'colores',
    'version': '0.1.2',
    'description': 'A Wrapper for Colorama',
    'long_description': '# Colores\n\nA simplifier of the [Colorama](https://github.com/tartley/colorama) API,\nand some extra functions.\n\n## Description\n\nColors was originally born in [Chuy](https://github.com/UltiRequiem/chuy).\nBut little by little, as I created more terminal applications\nI realized that in all of them I had some helper methods related to colorama,\nso I decided to separate it to a new package.\n\n## Usage\n\nIs very simple to use this package:\n\n```python\nfrom colores import colorized_print, colorized_input, CYAN, MAGENTA, YELLOW\n\ncolorized_print(colorized_input("Enter a text:"), CYAN)\n```\n\nAll the functions are defined in [colores/core.py](https://github.com/UltiRequiem/colores/blob/master/colores/core.py)\nand are well documented.\n\n### License\n\nThis project is licensed under the [MIT License](./LICENSE.md)\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/colores',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
