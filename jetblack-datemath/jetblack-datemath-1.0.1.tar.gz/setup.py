# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jetblack_datemath']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jetblack-datemath',
    'version': '1.0.1',
    'description': 'Date arithmetic for Python',
    'long_description': '# jetblack-datemath\n\nDate arithmetic for Python\n\n## Installation\n\n```bash\n$ pip install jetblack-datemath\n```\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/jetblack-datemath',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
