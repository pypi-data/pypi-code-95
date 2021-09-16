# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.flask']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.2.4,<2.0.0',
 'arcane-datastore>=1.0.0,<2.0.0',
 'arcane-pubsub>=1.0.0,<2.0.0',
 'backoff>=1.10.0,<2.0.0',
 'firebase_admin==4.1.0',
 'flask>=1.1.2,<2.0.0',
 'flask_log_request_id>=0.10.1,<0.11.0']

setup_kwargs = {
    'name': 'arcane-flask',
    'version': '1.1.2',
    'description': 'Utility functions for flask apps.',
    'long_description': "# Arcane flask\n\nThis package help us authenticate users\n\n## Get Started\n\n```sh\npip install arcane-flask\n```\n\n## Example Usage\n\n```python\nfrom arcane import flask\n\n@check_access_rights(service='function', required_rights='Viewer',\n                     receive_rights_per_client=True, project=Config.Project, adscale_key=Config.Key)\ndef function(params):\n    pass\n\n```\n\n",
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
