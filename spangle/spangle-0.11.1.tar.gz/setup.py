# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spangle', 'spangle.cli', 'spangle.models']

package_data = \
{'': ['*']}

install_requires = \
['addict>=2.2.1,<3.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'asgiref>=3.4.1,<4.0.0',
 'chardet>=4.0.0,<5.0.0',
 'httpx>=0.18.2,<0.19.0',
 'jinja2>=3.0.1,<4.0.0',
 'multidict>=5.1.0,<6.0.0',
 'multipart>=0.2.4,<0.3.0',
 'parse>=1.19.0,<2.0.0',
 'starlette>=0.15.0,<0.16.0',
 'urllib3>=1.26.6,<2.0.0']

entry_points = \
{'console_scripts': ['spangle = spangle.cli.run:main']}

setup_kwargs = {
    'name': 'spangle',
    'version': '0.11.1',
    'description': 'A small and flexible ASGI application framework for modern web.',
    'long_description': '---\nversion: v0.11.0\n---\n\n# spangle\n\n[![PyPI](https://img.shields.io/pypi/v/spangle)](https://pypi.org/project/spangle/)\n[![PyPI - License](https://img.shields.io/pypi/l/spangle)](https://pypi.org/project/spangle/)\n\nA small and flexible ASGI application framework for modern web.\n\nNote: `spangle` is on pre-alpha stage, so any updates may contain breaking changes.\n\n## Getting Started\n\n### Install\n\n```shell\npip install spangle\npip install hypercorn # or your favorite ASGI server\n```\n\n### Hello world\n\n```python\n# hello.py\nimport spangle\n\napi = spangle.Api()\n\n@api.route("/")\nclass Index:\n    async def on_request(self, req, resp):\n        resp.set_status(418).set_text("Hello world!")\n        return resp\n\n```\n\n```shell\nhypercorn hello:api\n```\n\n## Features\n\n- Components with dependencies\n- Flexible url params\n- `Jinja2` built-in support\n- Uniformed API\n- Single page application friendly\n\n...and more features. See [documents](http://tkamenoko.github.io/spangle).\n\n## Contribute\n\nContributions are welcome!\n\n- New features\n- Bug fix\n- Documents\n\n### Prerequisites\n\n- Python>=3.9\n- git\n- poetry\n\n### Build\n\n```shell\n# clone this repository.\ngit clone http://github.com/tkamenoko/spangle.git\n# install dependencies.\npoetry install\n```\n\n### Test\n\n```shell\npoetry run poe test\n```\n\n### Update API docs\n\n```shell\npoetry run poe doc:build\n```\n',
    'author': 'T.Kameyama',
    'author_email': 'tkamenoko@vivaldi.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tkamenoko/spangle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
