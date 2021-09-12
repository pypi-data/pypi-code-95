# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['imctools',
 'imctools.converters',
 'imctools.data',
 'imctools.io',
 'imctools.io.imc',
 'imctools.io.mcd',
 'imctools.io.ometiff',
 'imctools.io.txt']

package_data = \
{'': ['*']}

install_requires = \
['imagecodecs',
 'packaging',
 'pandas',
 'typing_extensions>=3.7.4.3',
 'xmltodict>=0.12.0',
 'xtiff>=0.7.4']

entry_points = \
{'console_scripts': ['imctools = imctools.cli:main']}

setup_kwargs = {
    'name': 'imctools',
    'version': '2.1.8',
    'description': 'Tools to handle Fluidigm IMC data',
    'long_description': '# imctools\n\n![PyPI](https://img.shields.io/pypi/v/imctools)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imctools)\n![PyPI - License](https://img.shields.io/pypi/l/imctools)\n![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/BodenmillerGroup/imctools/test-and-deploy/master)\n\nAn IMC file conversion tool that aims to convert IMC raw data files (.mcd, .txt) into an intermediary ome.tiff, containing all the relevant metadata. Further it contains tools to generate simpler TIFF files that can be directly be used as input files for e.g. CellProfiller, Ilastik, Fiji etc.\n\nDocumentation is available at [https://bodenmillergroup.github.io/imctools](https://bodenmillergroup.github.io/imctools)\n\n## Requirements\n\nThis package requires Python 3.7 or later.\n\nUsing virtual environments is strongly recommended.\n\n## Installation\n\nInstall imctools and its dependencies with:\n\n    pip install imctools\n\n## Usage\n\nSee [Quickstart](https://bodenmillergroup.github.io/imctools/quickstart.html)\n\n## Authors\n\nCreated and maintained by Vito Zanotelli [vito.zanotelli@uzh.ch](mailto:vito.zanotelli@uzh.ch) and Anton Rau [anton.rau@uzh.ch](mailto:anton.rau@uzh.ch)\n\n## Contributing\n\n[Contributing](https://bodenmillergroup.github.io/imctools/CONTRIBUTING.html)\n\n## Changelog\n\n[Changelog](https://bodenmillergroup.github.io/imctools/CHANGELOG.html)\n\n## License\n\n[MIT](https://bodenmillergroup.github.io/imctools/LICENSE.html)\n',
    'author': 'Vito Zanotelli',
    'author_email': 'vito.zanotelli@uzh.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BodenmillerGroup/imctools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
