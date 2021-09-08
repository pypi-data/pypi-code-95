# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['werkit',
 'werkit.aws_lambda',
 'werkit.common',
 'werkit.compute',
 'werkit.compute.destination',
 'werkit.orchestrator',
 'werkit.orchestrator.orchestrator_lambda',
 'werkit.orchestrator.testing',
 'werkit.orchestrator.testing.worker_service',
 'werkit.parallel',
 'werkit.scripts']

package_data = \
{'': ['*'],
 'werkit.compute': ['generated/*'],
 'werkit.orchestrator.orchestrator_lambda': ['generated/*'],
 'werkit.orchestrator.testing.worker_service': ['generated/*']}

install_requires = \
['jsonschema>=3.2.0,<4.0.0', 'semver==3.0.0.dev2', 'simplejson>=3.17.5,<4.0.0']

extras_require = \
{'aws_lambda_build': ['executor>=21.0'],
 'cli': ['click==8.0.1'],
 'client': ['boto3==1.17.69'],
 'lambda_common': ['harrison>=2.0,<3.0'],
 'parallel': ['redis==3.5.3'],
 'rds_graphile_worker': ['rds-graphile-worker-client>=0.1.1,<0.2.0']}

setup_kwargs = {
    'name': 'werkit',
    'version': '0.21.0',
    'description': 'Toolkit for encapsulating Python-based computation into deployable and distributable tasks',
    'long_description': None,
    'author': 'Paul Melnikow',
    'author_email': 'github@paulmelnikow.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://werkit.readthedocs.io/en/stable/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
