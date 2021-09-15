# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyphishtanklookup']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['phishtank-lookup = pyphishtanklookup:main']}

setup_kwargs = {
    'name': 'pyphishtanklookup',
    'version': '1.0',
    'description': 'Python CLI and module for PhishtankLookup',
    'long_description': '# PyPhishtank Lookup\n\nThis is the client API for [Phishtank Lookup](https://github.com/Lookyloo/phishtank-lookup),\nnot the official phishtank API.\n\n## Installation\n\n```bash\npip install pyphishtanklookup\n```\n\n## Usage\n\n### Command line\n\nYou can use the `phishtank-lookup` command to search in the database.\n\n### Library\n\nSee [API Reference]()\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lookyloo/PyPhishtankLookup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
