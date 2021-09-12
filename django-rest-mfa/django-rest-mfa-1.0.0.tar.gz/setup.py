# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_rest_mfa',
 'django_rest_mfa.mfa_admin',
 'django_rest_mfa.migrations',
 'django_rest_mfa.rest_auth_helpers']

package_data = \
{'': ['*'],
 'django_rest_mfa.mfa_admin': ['static/django_rest_mfa/*',
                               'templates/admin/*',
                               'templates/django_rest_mfa/*']}

install_requires = \
['dj-rest-auth>=2.1.7,<3.0.0',
 'djangorestframework>=3.12.4,<4.0.0',
 'fido2>=0.9.1,<0.10.0',
 'pyotp>=2.6.0,<3.0.0',
 'user-agents>=2.2.0,<3.0.0']

setup_kwargs = {
    'name': 'django-rest-mfa',
    'version': '1.0.0',
    'description': 'Django Rest Framework Endpoints for MFA including TOTP and FIDO2',
    'long_description': None,
    'author': 'David Burke',
    'author_email': 'david@burkesoftware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
