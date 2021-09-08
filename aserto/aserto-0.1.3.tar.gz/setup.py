# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aserto', 'aserto.api', 'aserto.api.authorizer']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'aserto-authorizer-grpc>=0.2.2,<0.3.0',
 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'aserto',
    'version': '0.1.3',
    'description': 'Aserto API client',
    'long_description': '# Aserto API client\nHigh-level client interface to Aserto\'s APIs.\n\nAt the moment this only supports interacting with Aserto\'s [Authorizer service](https://docs.aserto.com/authorizer-guide/overview).\n## Installation\n### Using Pip\n```sh\npip install aserto\n```\n### Using Poetry\n```sh\npoetry add aserto\n```\n## Usage\n```py\nfrom aserto import HostedAuthorizer, Identity\nfrom aserto.api.authorizer import AuthorizerClient\n\n\nclient = AuthorizerClient(\n    tenant_id=ASERTO_TENANT_ID,\n    identity=Identity(type="NONE"),\n    authorizer=HostedAuthorizer(api_key=ASERTO_API_KEY, service_type="gRPC"),\n)\n\nresult = await client.decision_tree(\n    decisions=["visible", "enabled", "allowed"],\n    policy_id=ASERTO_POLICY_ID,\n    policy_path_root=ASERTO_POLICY_PATH_ROOT,\n    policy_path_separator="DOT",\n)\n\nassert result == {\n    "GET.your.policy.path": {\n        "visible": True,\n        "enabled": True,\n        "allowed": False,\n    },\n}\n```',
    'author': 'Aserto, Inc.',
    'author_email': 'pypi@aserto.com',
    'maintainer': 'authereal',
    'maintainer_email': 'authereal@aserto.com',
    'url': 'https://github.com/aserto-dev/aserto-python/tree/HEAD/packages/aserto',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
