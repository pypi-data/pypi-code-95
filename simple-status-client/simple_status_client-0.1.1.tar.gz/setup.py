# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_status_client']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'yarl>=1.6.3,<2.0.0']

setup_kwargs = {
    'name': 'simple-status-client',
    'version': '0.1.1',
    'description': 'A package for interacting with the Simple Status Server',
    'long_description': '# SimpleStatusClient\n\nA helper Client library in Python for the SimpleStatus project\n\n## Getting Started\n\nEnsure you have pulled [SimpleStatusServer](https://github.com/bravosierra99/SimpleStatus) and are running it (preferably straight from docker)\n\n- clone library [SimpleStatusClient](https://github.com/bravosierra99/SimpleStatusClient)\n- cd SimpleStatusClient\n- python -m pip install . \\_(this should be the python environment in which your stasus needing code runs)\n- Within the code that you wish to send statuses do the following\n  - `from SimpleStatusClient import APIClient, Colors`\n  - `client = APIClient("http://*server_ip*/api")` server_ip should be the ip address of your docker container\n  - `client.setConfig()` -- _fill in params_\n  - `client.setStatus()` -- _fill in params_\n\nVoila, you should be able to view your status on the dashboard.\n\n### Example Usage\n\n`client.set_config("My Component","This is the thingamabob for our whatsamaahousit server", 0, Colors.yellow)`\n\n- <Response [200]>\n\n`client.set_status("My Component",Colors.green,"All systems go")`\n- <Response [200]>\n\n## Things to keep in mind\n- Components are identified by ID, which is calculated by hashing the name (or by calling the base functions and providing it directly e.g. `APIClient.set_status_base`).  \n  - *DUPLICATE NAMES OVERWRITE*.  \n  - This is by design, if you want to update your configuration and or status you can do it without jumping through any hoops.  Simply send a new configuration or status.  That being said if you have code in multiple places using the same id... they will be stepping on each other\n- This library is provided as a convience, the REST API is full accessible and you can write your own interface if you would like.  \n  - I promise to keep this library up to date and working to the best of my ability.  Maybe I\'ll even write tests for it.',
    'author': 'Benjamin Smith',
    'author_email': 'bravosierra99@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bravosierra99/SimpleStatusClient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
