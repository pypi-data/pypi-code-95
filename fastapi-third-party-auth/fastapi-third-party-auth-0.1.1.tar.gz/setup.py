# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_third_party_auth']

package_data = \
{'': ['*']}

install_requires = \
['cachetools>=4.1.1',
 'fastapi>=0.61.0',
 'pydantic>=1.6.1',
 'python-jose[cryptography]>=3.2.0',
 'requests>=2.24.0']

setup_kwargs = {
    'name': 'fastapi-third-party-auth',
    'version': '0.1.1',
    'description': 'Simple library for using a third party authentication service like Keycloak or Auth0 with FastAPI',
    'long_description': '# FastAPI Third Party Auth\n\n<p align="left">\n    <a href="https://github.com/aiwizo/fastapi-third-party-auth/actions?query=workflow%3ATest"\n       target="_blank">\n       <img src="https://github.com/aiwizo/fastapi-third-party-auth/workflows/Test/badge.svg"  \n            alt="Test">\n    </a>\n    <a href=\'https://fastapi-third-party-auth.readthedocs.io/en/latest/?badge=latest\'>\n        <img src=\'https://readthedocs.org/projects/fastapi-third-party-auth/badge/?version=latest\' alt=\'Documentation Status\' />\n    </a>\n    <a href="https://pypi.org/project/fastapi-third-party-auth" \n       target="_blank">\n       <img src="https://img.shields.io/pypi/v/fastapi-third-party-auth?color=%2334D058&label=pypi%20package" \n            alt="Package version">\n    </a>\n</p>\n\n---\n\n**Documentation**: <a href="https://fastapi-third-party-auth.readthedocs.io/" target="_blank">https://fastapi-third-party-auth.readthedocs.io/</a>\n\n**Source Code**: <a href="https://github.com/aiwizo/fastapi-third-party-auth" target="_blank">https://github.com/aiwizo/fastapi-third-party-auth</a>\n\n---\n\nSimple library for using a third party authentication service with \n[FastAPI](https://github.com/tiangolo/fastapi). Verifies and decrypts 3rd party\nOpenID Connect tokens to protect your endpoints.\n\nEasily used with authentication services such as:\n- [Keycloak](https://www.keycloak.org/) (open source)\n- [SuperTokens](https://supertokens.io/) (open source)\n- [Auth0](https://auth0.com/)\n- [Okta](https://www.okta.com/products/authentication/)\n\nFastAPI\'s generated interactive documentation supports the grant flows:\n```python3\nGrantType.AUTHORIZATION_CODE\nGrantType.IMPLICIT\nGrantType.PASSWORD\nGrantType.CLIENT_CREDENTIALS\n```\n\n![example documentation](example-docs.png)\n\n## Installation\n\n```\npoetry add fastapi-third-party-auth\n```\n\nOr, for the old-timers:\n\n```\npip install fastapi-third-party-auth\n```\n\n## Usage\n\nSee [this example](tree/master/example) for how to use\n`docker-compose` to set up authentication with `fastapi-third-party-auth` +\n[Keycloak](https://www.keycloak.org/).\n\n### Standard usage\n\n```python3\nfrom fastapi import Depends\nfrom fastapi import FastAPI\nfrom fastapi import Security\nfrom fastapi import status\n\nfrom fastapi_third_party_auth import Auth\nfrom fastapi_third_party_auth import GrantType\nfrom fastapi_third_party_auth import KeycloakIDToken\n\nauth = Auth(\n    openid_connect_url="http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration",\n    issuer="http://localhost:8080/auth/realms/my-realm",  # optional, verification only\n    client_id="my-client",  # optional, verification only\n    scopes=["email"],  # optional, verification only\n    grant_types=[GrantType.IMPLICIT],  # optional, docs only\n    idtoken_model=KeycloakIDToken,  # optional, verification only\n)\n\napp = FastAPI(\n    title="Example",\n    version="dev",\n    dependencies=[Depends(auth)],\n)\n\n@app.get("/protected")\ndef protected(id_token: KeycloakIDToken = Security(auth.required)):\n    return dict(message=f"You are {id_token.email}")\n```\n\n### Optional: Custom token validation\n\nThe IDToken class will accept any number of extra fields but you can also\nvalidate fields in the token like this:\n\n```python3\nclass MyAuthenticatedUser(IDToken):\n    custom_field: str\n    custom_default: float = 3.14\n\nauth = Auth(\n    ...,\n    idtoken_model=MyAuthenticatedUser,\n)\n```\n',
    'author': 'HarryMWinters',
    'author_email': 'harrymcwinters@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aiwizo/fastapi-third-party-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
