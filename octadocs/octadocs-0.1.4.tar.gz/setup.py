# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iolanta',
 'iolanta.cli',
 'iolanta.facets',
 'iolanta.loaders',
 'iolanta.parsers',
 'ldflex',
 'octadocs',
 'octadocs.cli',
 'octadocs.cli.formatters',
 'octadocs.facets',
 'octadocs.iolanta',
 'octadocs.navigation',
 'octadocs.octiron',
 'octadocs.octiron.plugins',
 'octadocs.pyld_document_loaders',
 'octadocs_adr',
 'octadocs_adr.facets']

package_data = \
{'': ['*'],
 'octadocs': ['yaml/*'],
 'octadocs_adr': ['templates/octadocs-decisions/*', 'yaml/*']}

install_requires = \
['PyLD>=2.0.3,<3.0.0',
 'backports.cached-property>=1.0.0,<2.0.0',
 'boltons>=21.0.0,<22.0.0',
 'classes>=0.4.0,<0.5.0',
 'deepmerge>=0.1.1,<0.2.0',
 'documented>=0.1.1,<0.2.0',
 'dominate>=2.6.0,<3.0.0',
 'graphviz>=0.17,<0.18',
 'mkdocs-macros-plugin>=0.5.0,<0.6.0',
 'mkdocs>=1.2,<1.3',
 'more-itertools>=8.9.0,<9.0.0',
 'owlrl>=5.2.1,<6.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pydotplus>=2.0.2,<3.0.0',
 'python-frontmatter>=0.5.0,<0.6.0',
 'rdflib-jsonld>=0.6.1,<0.7.0',
 'rdflib==5.0.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=10.3.0,<11.0.0',
 'singledispatchmethod>=1.0,<2.0',
 'typer>=0.3.2,<0.4.0',
 'typing-extensions>=3.7.4,<4.0.0',
 'urlpath>=1.1.7,<2.0.0']

entry_points = \
{'console_scripts': ['octadocs = octadocs.cli:app'],
 'mkdocs.plugins': ['octadocs = octadocs.plugin:OctaDocsPlugin',
                    'octadocs_adr = octadocs_adr.plugin:ADRPlugin']}

setup_kwargs = {
    'name': 'octadocs',
    'version': '0.1.4',
    'description': 'MkDocs wiki made smart',
    'long_description': '# octadocs\n\n[![Build Status](https://travis-ci.com/anatoly-scherbakov/octadocs.svg?branch=master)](https://travis-ci.com/anatoly-scherbakov/octadocs)\n[![Coverage](https://coveralls.io/repos/github/anatoly-scherbakov/octadocs/badge.svg?branch=master)](https://coveralls.io/github/anatoly-scherbakov/octadocs?branch=master)\n[![Python Version](https://img.shields.io/pypi/pyversions/octadocs.svg)](https://pypi.org/project/octadocs/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n## Features\n\n- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)\n- Add yours!\n\n\n## Installation\n\n```bash\npip install octadocs\n```\n\n## License\n\n[MIT](https://github.com/anatoly-scherbakov/octadocs/blob/master/LICENSE)\n\n\n## Credits\n\nThis project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [868260c2d659e455bafc2ed4fe242413ef39e4dc](https://github.com/wemake-services/wemake-python-package/tree/868260c2d659e455bafc2ed4fe242413ef39e4dc). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/868260c2d659e455bafc2ed4fe242413ef39e4dc...master) since then.\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/octadocs/octadocs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
