# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colorframe']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'joblib>=1.0,<2.0',
 'loguru>=0.5.1,<0.6.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['colorframe = colorframe.__main__:app']}

setup_kwargs = {
    'name': 'colorframe',
    'version': '0.2.1',
    'description': 'Python utility to add borders to my photography pictures',
    'long_description': '<h1 align="center">\n  <b>colorframe</b>\n</h1>\n\nA simple package to add a colored frame on pictures.\n\n## Install\n\nThis code is compatible with `Python 3.6+`.\nInstall it in your virtual enrivonment with:\n```bash\npip install colorframe\n```\n\n## Usage\n\nWith this package is installed in the activated enrivonment, it can be called through `python -m colorframe` or through a newly created `colorframe` command.\n\nDetailed usage goes as follows:\n```bash\nUsage: colorframe [OPTIONS] [PATH]\n\n  Add a colored frame on pictures, easily.\n\nArguments:\n  [PATH]  Location, relative or absolute, to the file or directory of files to\n          add a colored border to.\n\n\nOptions:\n  --vertical INTEGER    Size (width) of the whiteframe to add on the vertical\n                        image edges.  [default: 150]\n\n  --horizontal INTEGER  Size (height) of the whiteframe to add on the\n                        horizontal image edges.  [default: 150]\n\n  --color TEXT          The desired color of the added border. Should be a\n                        keyword recognized by Pillow.  [default: white]\n\n  --log-level TEXT      The base console logging level. Can be \'debug\',\n                        \'info\', \'warning\' and \'error\'.  [default: info]\n\n  --install-completion  Install completion for the current shell.\n  --show-completion     Show completion for the current shell, to copy it or\n                        customize the installation.\n\n  --help                Show this message and exit.\n```\n\nThe script will crawl files, add borders and export the results in a newly created `outputs` folder.\n\nYou can otherwise import the high-level object from the package, and use at your convenience:\n```python\nfrom colorframe import BorderCreator\n\nborder_api = BorderCreator(\n    commandline_pathp="path_to_your_images", vertical_border=150, horizontal_border=100, color="blue"\n)\nborder_api.execute_target()\n```\n\n---\n\n<div align="center">\n  <sub><strong>Made with ♥︎ by fsoubelet</strong></sub>\n  <br>\n  <sub><strong>MIT &copy 2020 Felix Soubelet</strong></sub>\n</div>\n',
    'author': 'Felix Soubelet',
    'author_email': 'felix.soubelet@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fsoubelet/toychain',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
