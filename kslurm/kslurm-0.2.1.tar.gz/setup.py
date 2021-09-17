# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kslurm',
 'kslurm.args',
 'kslurm.installer',
 'kslurm.models',
 'kslurm.slurm',
 'kslurm.style',
 'kslurm.submission']

package_data = \
{'': ['*'], 'kslurm': ['data/*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'colorama>=0.4.4,<0.5.0',
 'rich>=10.9.0,<11.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'typing-extensions>=3.10,<4.0']

entry_points = \
{'console_scripts': ['kbatch = kslurm.submission.kbatch:main',
                     'kjupyter = kslurm.submission.kjupyter:main',
                     'krun = kslurm.submission.kbatch.krun:main',
                     'kslurm = kslurm.kslurm:main']}

setup_kwargs = {
    'name': 'kslurm',
    'version': '0.2.1',
    'description': 'Helper scripts and wrappers for running commands on SLURM compute clusters.',
    'long_description': "This project is in a draft state.\n\nUtility functions to make working with SLURM easier. \n\n# Installation\nCluster utils is meant to be run in a SLURM environment, and thus will only install on linux. Open a shell and run the following command:\n\n```\ncurl -sSL https://raw.githubusercontent.com/pvandyken/kslurm/master/install_kslurm.py | python -\n```\n\nIf you wish to uninstall, run the same command with --uninstall added to the end.\n\n# Features\nCurrently offers two commands:\n* kbatch: for batch submission jobs (no immediate output)\n* krun: for interactive submission\n\nBoth support a regex-based argument parsing, meaning that instead of writing a SLURM file or supplying confusing --command-arguments, you can request resources with an intuitive syntax:\n\n```\nkrun 4 3:00 15G gpu \n```\nThis command will request interactive session with __4__ cores, for __3hr__, using __15GB__ of memory, and a gpu.\n\nYou could also add a command to run immediately:\n```\nkrun jupyter-lab '$(hostname)' --no-browser\n```\n\nYou can directly submit commands to kbatch without a script file:\n\n```\nkbatch 00:30 1000MB cp very/big/file.mp4 another/location\n```\n\nBoth kbatch and krun default to 1 core, for 3hr, with 4G of memory.\n\nYou can also run a predefined job template using -j _template_. Run either command with -J to get a list of all templates. Any template values can be overriden simply by providing the appropriate argument.\n\n",
    'author': 'Peter Van Dyken',
    'author_email': 'pvandyk2@uwo.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pvandyken/kslurm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
