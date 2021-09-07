# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jetblack_fincal']

package_data = \
{'': ['*']}

install_requires = \
['jetblack-datemath>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'jetblack-fincal',
    'version': '0.1.0',
    'description': 'Financial calendars',
    'long_description': '# jetblack-fincal\n\nFinancial calendars\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/jetblack-fincal',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
