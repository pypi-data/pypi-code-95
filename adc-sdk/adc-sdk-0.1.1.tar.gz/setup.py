# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['adc_sdk']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'gql==3.0.0a6',
 'requests>=2.26.0,<3.0.0',
 'typer>=0.3.2,<0.4.0',
 'websockets>=9.1,<10.0']

entry_points = \
{'console_scripts': ['adc = adc_sdk.cli:app']}

setup_kwargs = {
    'name': 'adc-sdk',
    'version': '0.1.1',
    'description': 'Argonne Discovery Cloud SDK and CLI',
    'long_description': "# Argonne Discovery Cloud SDK & CLI\n\n## Docs: \nhttps://stage.discoverycloud.anl.gov/docs/sdk/\n\n## Installation\n\n* When positioned in this repo's root directory:\n```\npip install adc-sdk\n```\n\n## CLI Commands\n```\nadc create-datafile\nadc create-investigation\nadc create-job\nadc create-sample\nadc create-study\nadc create-token\nadc current-user\nadc datafile\nadc delete-token\nadc investigation\nadc job\nadc remove-permissions\nadc sample\nadc set-permissions\nadc studies\nadc study\nadc subscribe-to-investigation\nadc subscribe-to-job\nadc subscribe-to-study\nadc tokens\nadc update-job\n```\nYou can run `adc <command> --help` for more information.\n\n\n## License\nThis project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details\n",
    'author': 'Argonne National Laboratory',
    'author_email': 'discovery@anl.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
