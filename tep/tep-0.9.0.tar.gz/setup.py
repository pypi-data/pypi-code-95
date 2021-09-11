# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tep']

package_data = \
{'': ['*']}

install_requires = \
['allure-pytest>=2.8.16,<3.0.0',
 'allure-python-commons>=2.8.16,<3.0.0',
 'faker>=4.1.1,<5.0.0',
 'jmespath>=0.10.0,<0.11.0',
 'loguru>=0.5.1,<0.6.0',
 'pytest-assume>=2.4.2,<3.0.0',
 'pytest-xdist>=2.2.1,<3.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'requests>=2.24.0,<3.0.0',
 'urllib3>=1.25.9,<2.0.0']

entry_points = \
{'console_scripts': ['tep = tep.cli:main'],
 'pytest11': ['tep = tep.plugin:Plugin']}

setup_kwargs = {
    'name': 'tep',
    'version': '0.9.0',
    'description': 'tep is a testing tool to help you write pytest more easily. Try Easy Pytest!',
    'long_description': '# tep\n\n`tep` is a testing tool to help you write pytest more easily. Try Easy Pytest!\n\n# Design Philosophy\n\n- Simple is better\n- Ready is better\n- Fast is better\n\n# Key Features\n\n- Inherit all features of `requests`，what `tep.client.request` adds is just a little log.\n- A single parameter `--tep-reports` generates the allure html test report.\n- Integrate common packages such as `faker`, `jmespath`, `loguru`, `pytest-xdist`, `pytest-assume`.\n- Provide a `requirements.txt` that contains some extension packages for optional manual installation.\n- The `fixtures` directory is automatically imported by `conftest.py`.\n\n# Installation\n\n`tep` is developed with Python, it supports Python `3.6+` and most operating systems.\n\n`tep` is available on [`PyPI`](https://pypi.python.org/pypi) and can be installed through `pip`:\n\n```\n$ pip install tep\n```\n\nor domestic mirror:\n\n```\n$ pip --default-timeout=600 install -i https://pypi.tuna.tsinghua.edu.cn/simple tep\n```\n\n# Check Installation\n\nWhen tep is installed, tep command will be added in your system.\n\nTo see `tep` version:\n\n```\n$ tep -V  # tep --version\n0.2.3\n```\n\n# Docs\n\n[fixture_env_vars a global variable](https://github.com/dongfanger/tep/blob/master/docs/fixture_env_vars%20a%20global%20variable.md)\n\n[fixture_login reuse a api](https://github.com/dongfanger/tep/blob/master/docs/fixture_login%20reuse%20a%20api.md)\n\n[websocket protobuf](https://github.com/dongfanger/tep/blob/master/docs/websocket%20protobuf.md)\n\n# Contact me\n\nWeChat: dongfangpy\n',
    'author': 'dongfanger',
    'author_email': 'dongfanger@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dongfanger/tep',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
