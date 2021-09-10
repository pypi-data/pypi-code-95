# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aioxiq', 'aioxiq.v1', 'aioxiq.v2']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.1,<0.19.0', 'tenacity>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'aio-xiq',
    'version': '0.3.1',
    'description': 'AsyncIO client for Extreme Cloud IQ',
    'long_description': '# Extreme Cloud IQ - Python3 AsyncIO Client\n\nThis repository contains a Python3 asyncio based client library for interacting\nwith the Extreme Cloud IQ system (XIQ).  The XIQ system supports a `v1` and `v2` client.  The `v2` API\nis Swagger defined and more _modern_; the `v1` API is more feature complete.\n\n### v2 API\n * [API Online Docts, Swagger](https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config)\n * [Github Repo](https://github.com/extremenetworks/ExtremeCloudIQ-APIs)\n\n### v1 API\n_May require a login account with the Extreme Developer Portal_:\n  * [API Online Docs](https://developer.aerohive.com/docs/api-documentation)\n',
    'author': 'Jeremy Schulman',
    'author_email': 'jeremy.schulman@mlb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jeremyschulman/aio-xiq',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
