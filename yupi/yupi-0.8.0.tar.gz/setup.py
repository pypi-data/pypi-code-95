# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yupi',
 'yupi.generators',
 'yupi.graphics',
 'yupi.stats',
 'yupi.tracking',
 'yupi.transformations']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5>=5.15.3,<6.0.0',
 'matplotlib>=3.2.0',
 'nudged>=0.3.1',
 'numpy>=1.16.5',
 'opencv-python>=4.4.0']

setup_kwargs = {
    'name': 'yupi',
    'version': '0.8.0',
    'description': 'A package for tracking and analysing objects trajectories',
    'long_description': '<p style="text-align:center;"><img src="logo.png" alt="Logo"></p>\n\nStanding for *Yet Underused Path Instruments*, **yupi** is a set of tools designed\nfor collecting, generating and processing trajectory data.\n\n## Installation\n\nCurrent recommended installation method is via the pypi package:\n\n```cmd\npip install yupi\n```\n\n## Getting Started\n\nIn the [official documentation](https://yupi.readthedocs.io/en/latest/) there\nare some resources to start using the library: Tutorials, Examples  and a\ndetailed description of the API.\n\n## Examples\n\nCode examples (with additional multimedia resources) can be found in\n[this repository](https://github.com/yupidevs/yupi_examples). Additionally, in\nthe [Examples section](https://yupi.readthedocs.io/en/latest/examples/examples.html)\nof the documentation, you can find the same examples with additional comments\nand expected execution results in order to inspect the examples without actually\nexecuting them.\n',
    'author': 'Gustavo Viera-López',
    'author_email': 'gvieralopez@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
