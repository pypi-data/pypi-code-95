# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['d2b_compile']
install_requires = \
['compile-dcm2bids-config>=1.0.0,<2.0.0', 'd2b>=1.0.0,<2.0.0']

entry_points = \
{'d2b': ['compile = d2b_compile']}

setup_kwargs = {
    'name': 'd2b-compile',
    'version': '1.0.0',
    'description': 'compile-dcm2bids-config plugin for the d2b package',
    'long_description': "# d2b-compile\n\ncompile-dcm2bids-config plugin for the d2b package.\n\n[![PyPI Version](https://img.shields.io/pypi/v/d2b-compile.svg)](https://pypi.org/project/d2b-compile/)\n\n## Installation\n\n```bash\npip install d2b-compile\n```\n\n## Usage\n\nAfter installation the `d2b run` command should have additional `compile`-subcommand:\n\n```text\n$ d2b --help\nusage: d2b [-h] [-v] {run,scaffold,compile} ...\n\nd2b - Organize data in the BIDS format\n\npositional arguments:\n  {run,scaffold,compile}\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -v, --version         show program's version number and exit\n```\n\n```text\n$ d2b compile --help\nusage: d2b compile [-h] [-o OUT_FILE] in_file [in_file ...]\n\npositional arguments:\n  in_file               The JSON config files to combine\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUT_FILE, --out-file OUT_FILE\n                        The file to write the combined config file to. If not specified outputs are written to stdout.\n```\n\nThe `d2b compile` subcommand is a thin wrapper around `compile-dcm2bids-config`.\n",
    'author': 'Alec Ross',
    'author_email': 'alexander.w.rosss@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/d2b-dev/d2b-compile',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
