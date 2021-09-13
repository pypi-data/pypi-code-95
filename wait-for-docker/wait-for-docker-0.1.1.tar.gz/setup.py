# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wait_for_docker']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.1,<6.0.0', 'yaspin>=2.1.0,<3.0.0']

entry_points = \
{'console_scripts': ['wait-for-docker = wait_for_docker.main:main']}

setup_kwargs = {
    'name': 'wait-for-docker',
    'version': '0.1.1',
    'description': 'A simple script to wait for Docker daemon to be active.',
    'long_description': "A simple script to wait for Docker daemon to be active.\n\n## Installation\n\n```bash\npython3 -m pip install wait-for-docker\n```\n\n## Usage\n\n```bash\nwait-for-docker && command_which_uses_docker\n```\n\nThe command waits until Docker daemon gets active. There's no configuration.\n",
    'author': 'Goto Hayato',
    'author_email': 'habita.gh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gh640/wait-for-docker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
