# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fortunekh']

package_data = \
{'': ['*']}

install_requires = \
['toolz>=0.11.1,<0.12.0']

entry_points = \
{'console_scripts': ['fortunekh = fortunekh.__main__:main']}

setup_kwargs = {
    'name': 'fortunekh',
    'version': '0.2.0',
    'description': 'Fortunekh',
    'long_description': '[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/KhalidCK/fortunekh)\n\n# README\n\n<!-- see readme-md-generator https://github.com/kefranabg/readme-md-generator -->\n',
    'author': 'Khalid CK',
    'author_email': 'fr.ckhalid@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
