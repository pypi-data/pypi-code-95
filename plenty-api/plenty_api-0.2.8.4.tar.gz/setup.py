# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plenty_api']

package_data = \
{'': ['*']}

install_requires = \
['keyring>=22.0.0,<23.0.0',
 'pandas>=1.1.2,<2.0.0',
 'python-gnupg>=0.4.6,<0.5.0',
 'requests>=2.24.0,<3.0.0',
 'simplejson>=3.17.2,<4.0.0',
 'tqdm>=4.60.0,<5.0.0']

setup_kwargs = {
    'name': 'plenty-api',
    'version': '0.2.8.4',
    'description': 'Interface for the PlentyMarkets API.',
    'long_description': "# Overview\n\nInterface for the PlentyMarkets API.\n\n# Setup\n\n## Requirements\n\n* Python 3.7.8+\n\n## Installation\n\nInstall it directly into an activated virtual environment:\n\n```text\n$ pip install python_plenty_api\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```text\n$ poetry add plenty_api\n```\n\n# Usage\n\nAfter installation, the package can imported:\n\n```text\n$ python\n>>> import plenty_api\n>>> plenty_api.__version__\n```\n## Examples\n\n```\nimport plenty_api\n\ndef main():\n    # Get the bearer token and set the basic attributes for an endpoint\n    plenty = plenty_api.PlentyApi(base_url='https://{your-shop}.plentymarkets-cloud01.com',  # available under setup->settings->API->data\n                                  use_keyring=True,  # Save the credentials into your system wide Keyring or not\n                                  data_format='json',  # Choose the output format (default JSON)\n                                  debug=True)  # display the constructed endpoint before making the request\n\n    orders = plenty.plenty_api_get_orders_by_date(start='2020-09-20',\n                                                  end='2020-09-24',\n                                                  date_type='payment',  # Get orders that were payed in between [start] and [end]\n                                                  additional=['documents', 'locations'],  # Include additional attributes to the response\n                                                  refine={'orderType': '1', 'referrerId': '1'})  # Only get orders with type 1 and from referrer 1\n\nif __name__ == '__main__':\n    main()\n```\n\n# Contact\n\nAuthor: Sebastian Fricke, Company: Panasiam, Email: sebastian.fricke.linux@gmail.com\n",
    'author': 'Sebastian Fricke',
    'author_email': 'sebastian.fricke@posteo.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/plenty_api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
