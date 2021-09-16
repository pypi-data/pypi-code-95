# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['classiq_interface',
 'classiq_interface.analyzer',
 'classiq_interface.backend',
 'classiq_interface.backend.ionq',
 'classiq_interface.chemistry',
 'classiq_interface.combinatorial_optimization',
 'classiq_interface.combinatorial_optimization.examples',
 'classiq_interface.executor',
 'classiq_interface.finance',
 'classiq_interface.generator',
 'classiq_interface.generator.preferences',
 'classiq_interface.generator.validations',
 'classiq_interface.hybrid',
 'classiq_interface.pyomo_extension',
 'classiq_interface.server']

package_data = \
{'': ['*']}

install_requires = \
['Pyomo>=6.0,<6.1',
 'more-itertools>=8.8.0,<9.0.0',
 'networkx>=2.5.1,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pillow>=8.3.1,<9.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'qiskit-terra>=0.18.1,<0.19.0']

setup_kwargs = {
    'name': 'classiq-interface',
    'version': '0.1.5',
    'description': 'Classiq Interface',
    'long_description': 'See [classiq package](https://pypi.org/project/classiq/) README.\n\n### License\nSee [license](https://classiq.io/license).\n',
    'author': 'Classiq Technologies',
    'author_email': 'support@classiq.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://classiq.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
