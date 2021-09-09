# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_dramatiq_email']

package_data = \
{'': ['*']}

install_requires = \
['django<3.3', 'django_dramatiq>0.9,<1.0', 'dramatiq>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'django-dramatiq-email',
    'version': '1.3.0',
    'description': 'A Django email backend using Dramatiq to send emails using background workers',
    'long_description': '# Django Dramatiq Email\n\nEmail backend for Django sending emails via Dramatiq.\n\n[![Test Status](https://github.com/SendCloud/django-dramatiq-email/workflows/Test/badge.svg?branch=master)](https://github.com/SendCloud/django-dramatiq-email/actions?query=workflow%3ATest)\n[![Lint Status](https://github.com/SendCloud/django-dramatiq-email/workflows/Lint/badge.svg?branch=master)](https://github.com/SendCloud/django-dramatiq-email/actions?query=workflow%3ALint)\n[![Code coverage Status](https://codecov.io/gh/SendCloud/django-dramatiq-email/branch/master/graph/badge.svg)](https://codecov.io/gh/SendCloud/django-dramatiq-email)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Installation\n\nTo enable `django-dramatiq-email` configure the Django `EMAIL_BACKEND` to `django_dramatiq_email.backends.DramatiqEmailBackend`\nand make sure add Django Dramatiq Email to your Django `INSTALLED_APPS`. This package is tested up to Django 3.\n\n## Configuration\n\nThe dramatiq task\'s configuration can be changed via the setting `DRAMATIQ_EMAIL_TASK_CONFIG` of type dict.\nBy default tasks are being pushed to the \'django_email\' queue. The settings in `DRAMATIQ_EMAIL_TASK_CONFIG`\nare being used at load time to construct the actor.\n\nExample configuration (using the Retry middleware):\n```\nDRAMATIQ_EMAIL_TASK_CONFIG = {\n    "max_retries": 20,\n    "min_backoff": 15000,\n    "max_backoff": 86400000,\n    "queue_name": "my_custom_queue"\n}\n```\n\nYou can change the actual email backend being used by changing `DRAMATIQ_EMAIL_BACKEND`.\n\n## Bulk emails\nBulk emails are send using individual Dramatiq tasks. Doing so these tasks can be restarted individually.\n\n## Maintainer\n[Tim Drijvers](http://github.com/timdrijvers)\n',
    'author': 'Tim Drijvers',
    'author_email': 'tim@sendcloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sendcloud/django-dramatiq-email',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
