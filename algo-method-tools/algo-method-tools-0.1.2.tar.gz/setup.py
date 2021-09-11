# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['algo_method_tools']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'requests>=2.26.0,<3.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['algo-tools = algo_method_tools.main:main']}

setup_kwargs = {
    'name': 'algo-method-tools',
    'version': '0.1.2',
    'description': 'algo-method用の環境構築用コマンドラインツール',
    'long_description': 'algo-method-tools\n===================\n\n![image](https://img.shields.io/pypi/v/algo-method-tools)\n![image](https://img.shields.io/pypi/pyversions/algo-method-tools)\n![image](https://img.shields.io/pypi/l/algo-method-tools)\n\nalgo-method用の環境構築用コマンドラインツール\n\n入力例, 出力例を含むディレクトリを自動生成する.\n\n**このプロジェクトの仕様は予告なしに変更される可能性があります (testコマンドに対応すると 変更されることが予想されます).**\n\n## インストール方法\n\n``` bash\n$ pip install algo-method-tools\n```\n\n\n## 使い方\n\n``` bash\n$ algo-tools --help\nUsage: algo-tools [OPTIONS] TASK_NO\n\nArguments:\n  TASK_NO  [required]\n\nOptions:\n  --base-dir PATH       [default: /home/yassu/algo-methods]\n  --template-file TEXT\n  --help                Show this message and exit.\n```\n\n\n## 使用例\n\n``` bash bash\n$ algo-tools 316\nwrite into /home/yassu/algo-methods/316\n$ cat ~/algo-methods/316/\nin_1.txt   main.py    out_1.txt\n$ cat ~/algo-methods/316/main.py\n$ cat ~/algo-methods/316/in_1.txt\n2 3\n1 2 3\n4 3 2\n$ cat ~/algo-methods/316/out_1.txt\n5\n\n\n# algo-tools/template.pyは自分用のテンプレートファイル\n$ algo-tools 316 --base-dir ~/repos/algo-tools --template-file ~/algo-tools/template.py\nwrite into /home/yassu/repos/algo-tools/316\n$ ls ~/repos/algo-tools/316/\nin_1.txt  main.py  out_1.txt\n$ cat ~/repos/algo-tools/316/main.py\nfrom pprint import pprint\nfrom sys import setrecursionlimit, stdin\nfrom typing import Dict, Iterable, Set\nINF: int = 2**62\n...\n$ cat ~/repos/algo-tools/316/in_1.txt\n2 3\n1 2 3\n4 3 2\n$ cat ~/repos/algo-tools/316/out_1.txt\n5\n```\n\n\n## オプション\n\n* `--template-file, -t`: 使用するテンプレートファイルを指定する(指定しなければ使用されない)\n* `--base-dir, -b`: ファイルを格納するディレクトリを指定する\n',
    'author': 'yassu',
    'author_email': 'yassu0320.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/yassu/algo-method-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
