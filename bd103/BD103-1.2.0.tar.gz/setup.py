# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bd103']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bd103',
    'version': '1.2.0',
    'description': "BD103's Python Package",
    'long_description': '# BD103 Python Package\n\nThese are some utility modules and fun stuff that might make a good dependency.\n\n## Java Version\n\nThere is a Java version of this package, go to [BD103-Java](https://github.com/BD103/BD103-Java)!',
    'author': 'BD103',
    'author_email': 'dont@stalk.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://bd103.github.io',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
