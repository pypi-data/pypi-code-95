# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webknossos',
 'webknossos.annotation',
 'webknossos.dataset',
 'webknossos.geometry',
 'webknossos.skeleton']

package_data = \
{'': ['*'], 'webknossos': ['client/*']}

install_requires = \
['attrs>=21.1.0,<22.0.0',
 'cattrs==1.7.1',
 'cluster_tools>=1.52,<2.0',
 'httpx>=0.15.4,<0.19.0',
 'numpy>=1.15.0,<2.0.0',
 'python-dateutil>=2.8.0,<3.0.0',
 'scikit-image>=0.16.0,<0.17.0',
 'scipy>=1.4.0,<2.0.0',
 'wkw==1.1.11']

setup_kwargs = {
    'name': 'webknossos',
    'version': '0.8.13',
    'description': 'Python package to work with webKnossos datasets and annotations',
    'long_description': '# webKnossos Python Library\n:construction:\n',
    'author': 'scalable minds',
    'author_email': 'hello@scalableminds.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
