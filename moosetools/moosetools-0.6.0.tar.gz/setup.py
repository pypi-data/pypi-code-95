# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['moosetools', 'moosetools.connect', 'moosetools.test']

package_data = \
{'': ['*']}

install_requires = \
['requests-toolbelt>=0.9.1,<0.10.0', 'requests>=2,<3']

setup_kwargs = {
    'name': 'moosetools',
    'version': '0.6.0',
    'description': 'Moose Tools',
    'long_description': '# moosetools\nTools and stuff\n',
    'author': 'Chuck Mo',
    'author_email': 'chuck@moosejudge.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://moosetools.moosejudge.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.9,<4.0.0',
}


setup(**setup_kwargs)
