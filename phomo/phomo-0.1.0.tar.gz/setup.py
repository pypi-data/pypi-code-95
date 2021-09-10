# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['phomo']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.2.0,<9.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'numpy>=1.20.2,<2.0.0',
 'tqdm>=4.60.0,<5.0.0']

extras_require = \
{':python_version ~= "3.7"': ['typing-extensions>=3.10.0,<4.0.0']}

entry_points = \
{'console_scripts': ['phomo = phomo.__main__:main']}

setup_kwargs = {
    'name': 'phomo',
    'version': '0.1.0',
    'description': 'Python package and CLI utility to create photo mosaics.',
    'long_description': '<h3 align="center"><img src="https://i.imgur.com/rMze8u5.png" width="1000"></h3>\n<h5 align="center">Python package and CLI utility to create photo mosaics.</h5>\n\n<p align="center">\n  <a href="https://github.com/loiccoyle/phomo/actions?query=workflow%3Atests"><img src="https://github.com/loiccoyle/phomo/workflows/tests/badge.svg"></a>\n  <a href="./LICENSE.md"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>\n  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-informational">\n</p>\n\n`phomo` lets you create [photographic mosaics](https://en.wikipedia.org/wiki/Photographic_mosaic).\nIt arranges the tile images to best recreate a master image. To acheive this, `phomo` computes a distance matrix between all the tiles and the master image regions, looking not just at the average colour but the norm of the colour distributions differences.\nOnce this distance matrix is computed, each tile is assigned to the region of the master with the smallest distance between the colour distributions.\n\n## Instalation\n\nRequires python 3\n\nIn a terminal:\n\n```sh\ngit clone https://github.com/loiccoyle/phomo\ncd phomo\npip install .\n```\n\n## Usage\n\n### Python package\n\nSee the [`examples`](./examples) folder for usage as a python package.\n\n### CLI\n\nOnce it is installed, you can use the `phomo` command.\n\nIt would go something like:\n\n```sh\n$ phomo master.png tile_directory -S 20 20 -o mosaic.png\n```\n\nIf in doubt see the help:\n\n```\nusage: phomo [-h] [-o OUTPUT] [-c MASTER_CROP_RATIO] [-s MASTER_SIZE [MASTER_SIZE ...]]\n              [-C TILE_CROP_RATIO] [-S TILE_SIZE [TILE_SIZE ...]] [-n N_APPEARANCES] [-v] [-b] [-g]\n              [-d SUBDIVISIONS [SUBDIVISIONS ...]]\n              master tile_dir\n\npositional arguments:\n  master                Master image path.\n  tile_dir              Directory containing the tile images.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUTPUT, --output OUTPUT\n                        Mosiac output path.\n  -c MASTER_CROP_RATIO, --master-crop-ratio MASTER_CROP_RATIO\n                        Crop the master image to width/height ratio.\n  -s MASTER_SIZE [MASTER_SIZE ...], --master-size MASTER_SIZE [MASTER_SIZE ...]\n                        Resize master image to width, height.\n  -C TILE_CROP_RATIO, --tile-crop-ratio TILE_CROP_RATIO\n                        Crop the tile images to width/height ratio.\n  -S TILE_SIZE [TILE_SIZE ...], --tile-size TILE_SIZE [TILE_SIZE ...]\n                        Resize tile images to width, height.\n  -n N_APPEARANCES, --n-appearances N_APPEARANCES\n                        The number of times a tile can appear in the mosaic.\n  -v, --verbose         Verbosity.\n  -b, --black_and_white\n                        Black and white.\n  -g, --show-grid       Show the tile grid, don\'t build the mosiac.\n  -d SUBDIVISIONS [SUBDIVISIONS ...], --subdivisions SUBDIVISIONS [SUBDIVISIONS ...]\n                        Subdivision thresholds.\n```\n\n## Note\n\nThe grid subdivision feature was inspired by [photomosaic](https://pypi.org/project/photomosaic/).\n\n## TODO:\n\n- [ ] look into non greedy tile assignements\n- [ ] look into parallelizing/multithreading\n- [ ] palette matching\n',
    'author': 'Loic Coyle',
    'author_email': 'loic.coyle@hotmail.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/loiccoyle/phomo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
