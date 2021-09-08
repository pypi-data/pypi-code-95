# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jetblack_graphql_types']

package_data = \
{'': ['*']}

install_requires = \
['graphql-core>=3.1.6,<4.0.0', 'jetblack-iso8601>=1.0,<2.0']

setup_kwargs = {
    'name': 'jetblack-graphql-types',
    'version': '0.2.0',
    'description': 'Serialization for JSON and XML using typing',
    'long_description': '# jetblack-graphql-types\n\nTypes for graphql\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/jetblack-graphql-types',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
