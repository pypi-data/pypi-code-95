# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['syneto_api']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3,<4',
 'aiohttp>=3.7,<4.0',
 'cchardet>=2.1,<3.0',
 'inflection>=0.5,<0.6',
 'python-dotenv>=0.16,<0.17',
 'requests[secure]>=2.25,<3.0']

setup_kwargs = {
    'name': 'syneto-api',
    'version': '0.2.43',
    'description': 'Syneto Client API library',
    'long_description': '# Syneto API\n\nSyneto Client API library: authentication, storage, virtualization and protection\n\n# Installation\n\n```\n$ pip install syneto-api\n```\n\n# Basic Usage\n\n```\nfrom syneto_api import Authentication, Virtualization, Storage, Protection\n\nauth_api = Authentication(url_base="https://syneto-instance-ip-address/api/auth", insecure_ssl=True)\nresponse = auth_api.login(username="admin", password="admin")\njwt = response[\'jwt\']\n\nvirt_api = Virtualization(url_base="https://syneto-instance-ip-address/api/virtualization", insecure_ssl=True)\nvirt_api.set_auth_jwt(jwt)\nprint(virt_api.get_vms())\n\nstorage_api = Storage(url_base="https://syneto-instance-ip-address/api/storage", insecure_ssl=True)\nstorage_api.set_auth_jwt(jwt)\nprint(storage_api.get_pools())\n```\n\n# Environment Variables\n\nFor conveninence, the base urls for the api endpoints are also accepted as environment variables, please see below.\n\n```\nAUTH_SERVICE=https://syneto-instance-ip-address/api/auth\nVIRTUALIZATION_SERVICE=https://syneto-instance-ip-address/api/virtualization\nSTORAGE_SERVICE=https://syneto-instance-ip-address/api/storage\nPROTECTION_SERVICE=https://syneto-instance-ip-address/api/protection\n```\n\nIf you are using self-signed SSL certificates, set the following env. so that the http request library does not perform ssl verification. \n\n```\nALLOW_INSECURE_SSL=True\n```\n',
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SynetoNet/syneto-api',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
