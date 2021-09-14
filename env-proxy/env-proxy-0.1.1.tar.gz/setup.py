# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['env_proxy']
setup_kwargs = {
    'name': 'env-proxy',
    'version': '0.1.1',
    'description': 'Creates a class used to query environmental variables with typehinting a conversion to basic Python types.',
    'long_description': '# EnvProxy\n\n`EnvProxy` provides a class used to query environmental variables with typehinting a conversion to basic Python types.\nYou can query your environment easily and keep your typehinting.\n\n## Installation\n\nUsing `pip`:\n\n```console\npip install env-proxy\n```\n\nUsing `poetry`:\n\n```console\npoetry add env-proxy\n```\n\n## Example\n\n```python\n# Import EnvProxy\nfrom env_proxy import EnvProxy\n\n# Basic examples\n## Environment variable "DATABASE_HOST"\ndatabase_host = EnvProxy.get_str("database-host")\n\n## If you want the function to fail if the value does not exist, use methods with `_strict` suffix\ndatabase_nonsene = EnvProxy.get_str_strict("database-nonsense")\n### ValueError: No value for key DATABASE_NONSENSE in environment\n\n## Specify default for the (non-zero) variable "DATABASE_PORT"\ndatabase_port = EnvProxy.get_int("database-port") or 5432\n\n# Specify custom prefix\nclass MyProxy(EnvProxy):\n    env_prefix: Optional[str] = "MYAPP"\n## Now all variables are expected to be prefixed with MYAPP_\ndatabase_host = EnvProxy.get_str("database-host")\n### Searches for MYAPP_DATABASE_HOST variable\n```\n\n## Documentation\n\nSee [docs](https://tomasvotava.github.io/env-proxy/)\n',
    'author': 'Tomas Votava',
    'author_email': 'info@tomasvotava.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tomasvotava/env-proxy',
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
