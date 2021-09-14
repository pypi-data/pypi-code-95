# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ezconda']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['ezconda = ezconda.main:app']}

setup_kwargs = {
    'name': 'ezconda',
    'version': '0.0.1',
    'description': 'Manage conda environments, write environment files and create conda lock files',
    'long_description': '# EZconda\n\n> Manage conda environments, write environment files and create conda lock files\n\n## Create new conda environment\n```bash\nezconda create -n new-env\n```\n\n## Install packages into environment\n\n```bash\nezconda install -n new-env python=3.9 numpy scipy matplotlib\n```',
    'author': 'Sarthak Jariwala',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
