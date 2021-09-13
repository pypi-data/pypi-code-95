# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omniblack', 'omniblack.repo']

package_data = \
{'': ['*'], 'omniblack.repo': ['model/*']}

install_requires = \
['anyio>=3.3.0,<4.0.0',
 'atpublic>=2.3,<3.0',
 'omniblack.model[yaml]>=0.1.17,<0.2.0',
 'python-box[ruamel.yaml,toml]>=5.4.1,<6.0.0']

setup_kwargs = {
    'name': 'omniblack.repo',
    'version': '0.0.3',
    'description': 'Tooling for interacting with monorepos.',
    'long_description': '# Omniblack Repo\n\nOmniblack Repo offers tools for interacting with a monorepo.\n',
    'author': 'Terry Patterson',
    'author_email': 'terryp@wegrok.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
