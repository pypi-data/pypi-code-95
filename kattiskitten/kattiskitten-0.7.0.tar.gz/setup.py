# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kattiskitten', 'kattiskitten.languages']

package_data = \
{'': ['*']}

install_requires = \
['click==7.0', 'colorful==0.5.4', 'requests==2.22.0']

entry_points = \
{'console_scripts': ['kk = kattiskitten:main']}

setup_kwargs = {
    'name': 'kattiskitten',
    'version': '0.7.0',
    'description': 'Kattis CLI - Easily download, test and submit kattis problems',
    'long_description': "# Kattis kitten\n![Repo size](https://img.shields.io/github/repo-size/FelixDQ/kattis-kitten)\n[![PyPI version](https://img.shields.io/pypi/v/kattiskitten)](https://pypi.org/project/kattiskitten/)\n\nKattis CLI - Easily download, test and submit kattis problems\n```\nUsage: kk [OPTIONS] COMMAND [ARGS]...\n\n  Simple CLI for downloading and testing kattis problems\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  get       This command downloads a kattis problem and test files\n  problems  Simply opens https://open.kattis.com/problems in your webbrowser\n  submit    This command submits a problem to kattis\n  test      This tests a kattis problem using provided test problems\n```\nInstallation (requires python >= 3.6):\n```\npip3 install kattiskitten\n```\n\n# Commands\nDownload test files.\n```\n> kk get rationalsequence\nDownloading samples\nSamples downloaded to './rationalsequence'\n```\n\nTest the problem\n```\n> kk test rationalsequence\n👷\u200d Testing rationalsequence...\n👷\u200d Language = Python 3 🐍\n\n🔎 Test number 1:\n❌ Failed...\n__________INPUT____________\n5\n1 1/1\n2 1/3\n3 5/2\n4 2178309/1346269\n5 1/10000000\n\n__________INPUT____________\n__________OUTPUT___________\nHello world!\n\n__________OUTPUT___________\n__________EXPECTED_________\n1 1/2\n2 3/2\n3 2/5\n4 1346269/1860498\n5 10000000/9999999\n\n__________EXPECTED_________\n```\n\nSubmit solution to kattis\n```\n> kk submit rationalsequence\nSubmission received. Submission ID: 5030066.\n* Opens web browser on submission page *\n```\n# Choose language\nThe default language is python3. To change language you can use the `--language` flag on the get command.\n```\n> kk get rationalsequence --language java\nDownloading samples\nSamples downloaded to './rationalsequence'\n```\nThe other commands will auto detect which language you have chosen.\n\n# Supported languages\n* Python3\n* Java\n* C++\n* C\n* Contribute by adding [more languages](https://github.com/FelixDQ/kattis-kitten/tree/master/kattiskitten/languages)! :-) \n",
    'author': 'Felix Qvist',
    'author_email': 'felix@qvist.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FelixDQ/kattis-kitten',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
