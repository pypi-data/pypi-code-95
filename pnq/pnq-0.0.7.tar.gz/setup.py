# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pnq']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pnq',
    'version': '0.0.7',
    'description': '',
    'long_description': '<h1 align="center" style="font-size: 3rem; margin: -15px 0">\nPNQ\n</h1>\n\n---\n\n<div align="center">\n<p>\n<a href="https://github.com/sasano8/pnq/actions">\n    <img src="https://github.com/sasano8/pnq/actions/workflows/test.yml/badge.svg" alt="Test Suite">\n</a>\n<a href="https://pypi.org/project/pnq/">\n    <img src="https://badge.fury.io/py/pnq.svg" alt="Package version">\n</a>\n</p>\n\n<em>User-friendly collection manipulation library.</em>\n</div>\n\nPNQ is a Python implementation like Language Integrated Query (LINQ).\n\nhttps://pypi.org/project/pnq/\n\n!!! danger\n    PNQはベータ版です。\n\n    - 現在、ドキュメントとAPIが一致していません。\n    - PNQは鋭意開発中でAPIが頻繁に変更される恐れがあるため、本番環境では利用しないでください。\n\n---\n\n\n\n## Features\n\n- コレクション操作に関する多彩な操作\n- アクセシブルなインターフェース\n- 型ヒントの活用\n\n## Documentation\n\n\n\n## Dependencies\n\n- Python 3.7+\n\n## Installation\n\nInstall with pip:\n\n```shell\n$ pip install pnq\n```\n\n## Getting Started\n\n```python\nimport pnq\n\npnq.query([1]).map(lambda x: x * 2).to_list()\n# >> [2]\n\npnq.query({"a": 1, "b": 2}).filter(lambda x: x[0] == "a").to_list()\n# >> [("a", 1)]\n\n```\n\n## release note\n\n### v0.0.1 (2021-xx-xx)\n\n* Initial release.',
    'author': 'sasano8',
    'author_email': 'y-sasahara@ys-method.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
