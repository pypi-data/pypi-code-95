# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['github_activity_visualiser']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0', 'click>=8.0.1,<9.0.0']

entry_points = \
{'console_scripts': ['visualiser = github_activity_visualiser.visualiser:cli']}

setup_kwargs = {
    'name': 'github-activity-visualiser',
    'version': '0.1.1',
    'description': '',
    'long_description': "Github user activity visualiser \n---\n- download all user's public repositories\n- filter forks and mirrors\n- build a one year activity log\n- run a gource on it\n\n[more details (rus)](https://habrahabr.ru/company/semrush/blog/345818/)\n\n![КДПВ](https://habrastorage.org/webt/jq/os/wn/jqoswnphohklp8eswtsejbgtxty.gif)\n\n### Usage\n\nU need [token](https://github.com/settings/tokens) for this tool\ntodo\n\n### Run from source\n```\n$ git clone https://github.com/esemi/github-activity-visualiser.git\n$ cd github-activity-visualiser\n$ python3.9 -m venv venv\n$ source venv/bin/activate\n$ pip install poetry\n$ poetry config virtualenvs.create false --local\n$ poetry install\n$ apt install gource\n$ poetry run python github_activity_visualiser/visualiser.py --help\n```\n",
    'author': 'Simon',
    'author_email': 'spam@esemi.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/esemi/github-activity-visualiser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
