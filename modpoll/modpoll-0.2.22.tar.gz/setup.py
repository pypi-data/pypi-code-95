# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modpoll']

package_data = \
{'': ['*']}

install_requires = \
['paho-mqtt>=1.5.1,<2.0.0', 'pymodbus>=2.5.2,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['modpoll = modpoll:app']}

setup_kwargs = {
    'name': 'modpoll',
    'version': '0.2.22',
    'description': 'A command line tool to communicate with modbus devices',
    'long_description': '[![pipeline status](https://gitlab.com/helloysd/modpoll/badges/master/pipeline.svg)](https://gitlab.com/helloysd/modpoll/-/commits/master)\n[![License](https://img.shields.io/pypi/l/modpoll)](https://gitlab.com/helloysd/modpoll/-/blob/master/LICENSE)\n[![Downloads](https://img.shields.io/pypi/dm/modpoll)](https://pypi.org/project/modpoll)\n\n---\n\n## Modpoll\n\nA command line tool to communicate with modbus devices.\n\n> Learn more about `modpoll` usage at [documentation](https://helloysd.gitlab.io/modpoll) site. \n\n\n### Installation\n\nThis program is tested on python 3.6+.\n\n- Install with pip\n\n  The package is available in the Python Package Index, \n\n  ```bash\n  pip install modpoll\n  ```\n\n- Upgrade to the latest version\n\n  It is recommended to upgrade if a new version is available,\n\n  ```bash\n  pip install -U modpoll\n  ```\n\n### Examples\n\nPlease refer to [documentation](https://helloysd.gitlab.io/modpoll) site for more configures and examples.\n',
    'author': 'Ying Shaodong',
    'author_email': 'helloysd@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://helloysd.gitlab.io/modpoll',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
