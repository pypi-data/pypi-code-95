# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['os2mo_dar_client']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'more-itertools>=8.8.0,<9.0.0',
 'ra-utils>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'os2mo-dar-client',
    'version': '0.1.0',
    'description': 'OS2mo DAR Client is a client for DAWA / DAR',
    'long_description': '<!--\nSPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>\nSPDX-License-Identifier: MPL-2.0\n-->\n\n# OS2mo DAR Client\n\nOS2mo DAR Client is a client for [DAWA / DAR](https://dawadocs.dataforsyningen.dk/).\n\n## Requirements\n\nPython 3.8+\n\nDependencies:\n\n* <a href="https://more-itertools.readthedocs.io/" class="external-link" target="_blank">More Itertools</a>\n* <a href="https://docs.aiohttp.org/en/stable/" class="external-link" target="_blank">AIOHTTP</a>\n* <a href="https://rammearkitektur.docs.magenta.dk/ra-utils/index.html" class="external-link" target="_blank">RA Utils</a>\n\n## Installation\n\n```console\n$ pip install os2mo-dar-client\n```\n\n## Usage\n```Python\nfrom os2mo_dar_client import DARClient\n\ndarclient = DARClient()\nwith darclient:\n    print(darclient.healthcheck())\n```\n\n## License\n\nThis project is licensed under the terms of the MPL-2.0 license.\n',
    'author': 'Magenta',
    'author_email': 'info@magenta.dk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://magenta.dk/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
