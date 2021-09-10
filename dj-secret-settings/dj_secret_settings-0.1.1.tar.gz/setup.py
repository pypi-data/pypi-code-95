# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dj_secret_settings',
 'dj_secret_settings.fetchers',
 'dj_secret_settings.stores']

package_data = \
{'': ['*']}

extras_require = \
{'google_secret_manager': ['google-cloud-secret-manager>=2.7.0,<3.0.0']}

setup_kwargs = {
    'name': 'dj-secret-settings',
    'version': '0.1.1',
    'description': 'Provide settings to Django from a secret store such as Google Cloud Secrets',
    'long_description': 'Yet Another Django Settings Helper\n==================================\n\nThis library allows secret settings to be easily changed for dev/Staging/Production etc purposes. e.g. One might obtain development settings from the process environment but later deploy to _Google Compute Engine_ where use of *_Google Secret Manager_* is recommended. If the app later finds its way onto _AWS_, a suitable fetcher can be installed or written.\n\nI tend to put all the secret settings for an environment in a single secret as a JSON document, for cost and convenience. You can also put non-secret settings in the same document or install them as environment variables as you prefer.\n\n** I have no affiliation with Google, Amazon or any other cloud computing provider! **\n\n## Installation\n\n    pip install dj_secret_settings\n\n## Configuration\n\nInstall settings fetchers to get the raw data from the store, and settings stores to make sense of the raw data and return pieces of it on demand.\n\nThe package can be configured with a string or by using the environment variable `DJ_SECRET_SETTINGS_URL` with the form:\n\n    store_type+fetcher_type://information.used.by/the/fetcher/and/or/the/store_type?like_a=url\n\ne.g. `json+gsm://anything-here-perhaps-service-account/projects/123456789/secrets/my-secret/versions/42` indicates that data will be fetched from _Google Secret Manager_\\* and interpreted as a JSON string.\n\n\\* configuration of this is obviously required too, contact me if you need help with that.\n\nThe package includes a _Google Secret Manager_ fetcher, with JSON and environment variable store types. These can be overridden by installing a root package of the form dj_secret_settings_{store_type} (e.g. dj_secret_settings_json) or dj_secret_settings_{fetcher_type} (e.g dj_secret_settings_gsm). Alternatively you can install differently named root packages and modifiy the URL (e.g dj_secret_settings_yaml for a yaml store using the URL of the form yaml+gsm://...).\n\n## Usage\n\n    from dj_secret_settings import settings_store\n    store = settings.store.load("json+gsm://anything-here-perhaps-service-account/projects/123456789/secrets/my-secret/versions/42")\n\n    MAX_SIZE = store.get_value(\'MAX_SIZE\', default=314, coerce_type=int)\n    IS_PRODUCTION = store.get_boolean(\'is_production\', default=FALSE)\n    MY_LIST = store.get_array(\'MY_LIST\')\n    A_MAP = store.get_mapping(\'A_MAP\', default={})\n\n`default`s are always optional, as is `coerce_type` on `get_value`\n',
    'author': 'Steven Davidson',
    'author_email': 'github@damycra.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/damycra/dj_secret_settings',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
