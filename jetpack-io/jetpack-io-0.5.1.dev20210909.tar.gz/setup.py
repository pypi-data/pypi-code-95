# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jetpack',
 'jetpack._job',
 'jetpack._remote',
 'jetpack.config',
 'jetpack.models',
 'jetpack.models.core',
 'jetpack.models.runtime',
 'jetpack.proto.runtime.v1alpha1']

package_data = \
{'': ['*']}

install_requires = \
['cronitor>=4.2.0,<5.0.0',
 'grpcio>=1.37.1,<2.0.0',
 'jsonpickle>=2.0.0,<3.0.0',
 'protobuf>=3.17.0,<4.0.0',
 'redis-namespace>=3.0.1,<4.0.0',
 'redis==3.0.1',
 'schedule>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'jetpack-io',
    'version': '0.5.1.dev20210909',
    'description': 'Python SDK for Jetpack.io',
    'long_description': '\n## Build SDK\n\nRun `./devtools/scripts/sdk/python/build.sh`.\n\nThis will produce SDK distributions in `sdk/python/dist`.\n\n## Run tests\n\n```\n# Pre-requisite: build the SDK using the command above.\n\ncd sdk/python/tests\npoetry run pytest\n```\n',
    'author': 'jetpack.io',
    'author_email': 'hello@jetpack.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.jetpack.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
