# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyzscaler', 'pyzscaler.zia', 'pyzscaler.zpa']

package_data = \
{'': ['*']}

install_requires = \
['python-box>=5.4.1,<6.0.0', 'restfly>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'pyzscaler',
    'version': '0.8.0',
    'description': 'A python SDK for the Zscaler API.',
    'long_description': '# pyZscaler - An unofficial SDK for the Zscaler API\n\n[![Documentation Status](https://readthedocs.org/projects/pyzscaler/badge/?version=latest)](http://pyzscaler.readthedocs.io/?badge=latest)\n[![](https://img.shields.io/github/license/mitchos/pyZscaler.svg)](https://github.com/mitchos/pyZscaler)\n[![](https://app.codacy.com/project/badge/Grade/d339fa5d957140f496fdb5c40abc4666)](https://www.codacy.com/gh/mitchos/pyZscaler/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mitchos/pyZscaler&amp;utm_campaign=Badge_Grade)\n[![](https://img.shields.io/pypi/v/pyzscaler.svg)](https://pypi.org/project/pyZscaler)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyzscaler.svg)](https://pypi.python.org/pypi/pyzscaler/)\n[![GitHub release](https://img.shields.io/github/release/mitchos/pyZscaler.svg)](https://github.com/mitchos/pyZscaler/releases/)\n\npyZscaler is an SDK that provides a uniform and easy-to-use interface for each of the Zscaler product APIs.\n\nThis SDK is not affiliated with, nor supported by Zscaler in any way.\n\n## Installation\n\nThe most recent version can be installed from pypi as per below.\n\n    $ pip install pyzscaler\n\n## Usage\n\nYou may need to generate API keys or retrieve tenancy information\nfor each product that you are interfacing with. Once you have the requirements and you have installed pyZscaler,\nyou\'re ready to go.\n\n\n### Quick ZIA Example\n\n    from pyzscaler.zia import ZIA\n    from pprint import pprint\n\n    zia = ZIA(api_key=\'API_KEY\', cloud=\'CLOUD\', username=\'USERNAME\', password=\'PASSWORD\')\n    for user in zia.users.list():\n        pprint(user)\n\n### Quick ZPA Example\n\n    from pyzscaler.zpa import ZPA\n    from pprint import pprint\n\n    zpa = ZPA(client_id=\'CLIENT_ID\', client_secret=\'CLIENT_SECRET\', customer_id=\'CUSTOMER_ID\')\n    for app_segment in zpa.app_segments.list():\n        pprint(app_segment)\n\n## Contributing\n\nPlease see the [Contribution Guidelines](https://github.com/mitchos/pyZscaler/blob/main/CONTRIBUTING.md) for more information.\n\n## Issues\nPlease feel free to open an issue using [Github Issues](https://github.com/mitchos/pyZscaler/issues) if you run into any problems using pyZscaler.\n\n## License\nMIT License\n\nCopyright (c) 2021 Mitch Kelly\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.',
    'author': 'Mitch Kelly',
    'author_email': 'me@mkelly.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mitchos.github.io/pyZscaler/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
