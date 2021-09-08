# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyclonedx', 'cyclonedx.model', 'cyclonedx.output', 'cyclonedx.parser']

package_data = \
{'': ['*'], 'cyclonedx': ['schema/*', 'schema/ext/*']}

install_requires = \
['importlib-metadata>=4.8.1,<5.0.0',
 'packageurl-python>=0.9.4,<0.10.0',
 'requirements_parser>=0.2.0,<0.3.0',
 'setuptools>=50.3.2,<51.0.0']

setup_kwargs = {
    'name': 'cyclonedx-python-lib',
    'version': '0.0.8',
    'description': 'A library for producing CycloneDX SBOM (Software Bill of Materials) files.',
    'long_description': None,
    'author': 'Paul Horton',
    'author_email': 'phorton@sonatype.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
