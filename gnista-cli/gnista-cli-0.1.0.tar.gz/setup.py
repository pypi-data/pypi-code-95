# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gnista_cli']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0',
 'elevate>=0.1.3,<0.2.0',
 'gnista-library>=1.0.9,<2.0.0',
 'structlog>=21.1.0,<22.0.0']

setup_kwargs = {
    'name': 'gnista-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': '[![Gitlab Pipeline](https://gitlab.com/campfiresolutions/public/gnista.io-cli/badges/main/pipeline.svg)](https://gitlab.com/campfiresolutions/public/gnista.io-cli/-/pipelines)  [![Python Version](https://img.shields.io/pypi/pyversions/gnista-cli)](https://pypi.org/project/gnista-cli/)  [![PyPI version](https://img.shields.io/pypi/v/gnista-cli)](https://pypi.org/project/gnista-cli/)  [![License](https://img.shields.io/pypi/l/gnista-cli)](https://pypi.org/project/gnista-cli/)  [![Downloads](https://img.shields.io/pypi/dm/gnista-cli)](https://pypi.org/project/gnista-cli/) \n\n# gnista-cli\nA cli for accessing gnista.io\n\n# Installing\nInstall gnista-cli for all Users, remove `-a` if you want to install for your current user only\n``` bash\npip install gnista-cli\npython -m gnista_cli i -a\n```\n\n# Opening Custom URL Protocol\nThe commandline is able to handle `hgnista` URLs and redirect them to a specific client.\n\nIn this example it opens the datapoint `45623780-6a9a-45e6-a522-650d4484a019`in `Visplore`\n``` bash\npython -m gnista_cli o hgnista://45623780-6a9a-45e6-a522-650d4484a019?client=visplore\n```\n\n\n## Links\n**Website**\n[![gnista.io](https://www.gnista.io/assets/images/gnista-logo-small.svg)](gnista.io)\n\n**PyPi**\n[![PyPi](https://pypi.org/static/images/logo-small.95de8436.svg)](https://pypi.org/project/gnista-cli/)\n\n**GIT Repository**\n[![Gitlab](https://about.gitlab.com/images/icons/logos/slp-logo.svg)](https://gitlab.com/campfiresolutions/public/gnista.io-cli)',
    'author': 'Markus Hoffmann',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gnista.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
