# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['levocli',
 'levocli.apitesting',
 'levocli.apitesting.runs',
 'levocli.handlers',
 'levocli.modules',
 'levocli.modules.plans',
 'levocli.modules.plans.handlers',
 'levocli.modules.schemathesis',
 'levocli.modules.schemathesis.handlers']

package_data = \
{'': ['*']}

install_requires = \
['click-loglevel>=0.4.0,<0.5.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.4,<0.5.0',
 'grpcio>=1.37.0,<2.0.0',
 'levo-commons>=0.1.3,<0.2.0',
 'protobuf>=3.15.8,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'questionary>=1.10.0,<2.0.0',
 'reportportal-client>=5.0.10,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'schemathesis>=3.9.7,<4.0.0',
 'sgqlc>=14.0,<15.0',
 'structlog>=21.1.0,<22.0.0']

entry_points = \
{'console_scripts': ['levo = levocli.cli:levo']}

setup_kwargs = {
    'name': 'levo',
    'version': '0.3.1',
    'description': "Levo.ai's CLI that users can use to automatically trigger functional and security testing of their APIs.",
    'long_description': None,
    'author': 'Buchi Reddy B',
    'author_email': 'buchi@levo.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
