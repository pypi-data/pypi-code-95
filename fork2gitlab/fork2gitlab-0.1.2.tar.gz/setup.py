# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fork2gitlab', 'fork2gitlab.commands']

package_data = \
{'': ['*']}

install_requires = \
['cliff>=3.1.0,<4.0.0', 'python-gitlab>=2.1.2,<3.0.0']

entry_points = \
{'console_scripts': ['f2g = fork2gitlab.main:main']}

setup_kwargs = {
    'name': 'fork2gitlab',
    'version': '0.1.2',
    'description': 'A script to help forking a project to gitlab and keeping it updated downstream',
    'long_description': "A script to help forking a project to gitlab and keeping it updated downstream\n\n# Installation\n\n`pip install fork2gitlab`\n\n# Configuration\n\nIn order to interact with the gitlab instance, a configuration file will be needed.\nCreate on in on the [locations supported by python-gitlab][python-gitlab locations]\n\n# Usage\n\n**Forking**\n\nUse `f2g fork <git url>` to import a git project.\n\nThe project will also be automatically mirrored hourly by gitlab.\n\nYou can then create your branch and make changes. \n\n**Syncing**\n\nUse `f2g sync <gitlab project name> <branch>` to merge upstream changes into your branch.\n\nSince gitlab takes care of the hourly sync, this command simply attempts to merge the upstream changes.\nWhen a merge conflict occurs, a merge request will be created.\n\nIt's up to you to notify in case the merge request has been created. \n\n[python-gitlab locations]: https://python-gitlab.readthedocs.io/en/stable/cli.html#configuration\n",
    'author': 'LoveIsGrief',
    'author_email': 'loveisgrief@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/NamingThingsIsHard/collaboration/fork2gitlab',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
