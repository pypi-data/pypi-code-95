# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_sessions',
 'fastapi_sessions.backends',
 'fastapi_sessions.backends.implementations',
 'fastapi_sessions.frontends',
 'fastapi_sessions.frontends.implementations']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.65,<0.66', 'itsdangerous>=2.0.1,<3.0.0']

extras_require = \
{'dev': ['flake8>=3.9.0,<4.0.0',
         'flake8-docstrings>=1.6.0,<2.0.0',
         'black>=20.8b1,<21.0',
         'uvicorn>=0.14.0,<0.15.0',
         'pytest>=6.2.3,<7.0.0',
         'isort>=5.9.3,<6.0.0'],
 'docs': ['mkdocs-material>=7.1.0,<8.0.0', 'markdown-include>=0.6.0,<0.7.0']}

setup_kwargs = {
    'name': 'fastapi-sessions',
    'version': '0.3.1',
    'description': 'Ready-to-use session library for FastAPI',
    'long_description': "# FastAPI-Sessions\n\n\n---\n\nDocumentation: [https://jordanisaacs.github.io/fastapi-sessions/](https://jordanisaacs.github.io/fastapi-sessions/)\n\nSource Code: [https://github.com/jordanisaacs/fastapi-sessions/](https://github.com/jordanisaacs/fastapi-sessions/)\n\nPyPI: [https://pypi.org/project/fastapi-sessions/](https://pypi.org/project/fastapi-sessions/)\n\n---\n\nQuickly add session authentication to your FastAPI project. **FastAPI Sessions** is designed to be user friendly and customizable.\n\n\n## Features\n\n- [x] Dependency injection to protect routes\n- [x] Compatible with FastAPI's auto generated docs\n- [x] Pydantic models for verifying session data\n- [x] Abstract session backend so you can build one that fits your needs\n- [x] Abstract frontends to choose how you extract the session ids (cookies, header, etc.)\n- [x] Create verifiers based on the session data\n- [x] Mix and match frontends and backends\n\nCurrently Included Backends/Frontends:\n\n- [x] Backends\n    - [x] In memory dictionary\n- [x] Frontends\n    - [x] Signed cookies\n\n\nUpcoming:\n\n* Documentation and user guides\n* More backends and frontends\n\n## Installation\n\n```python\npip install fastapi-sessions\n```\n\n## Getting Started\n\nCheck out the guide to using fastapi-sessions: [https://jordanisaacs.github.io/fastapi-sessions/guide/getting_started/](https://jordanisaacs.github.io/fastapi-sessions/guide/getting_started/)\n",
    'author': 'Jordan Isaacs',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jordanisaacs/fastapi-sessions',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
