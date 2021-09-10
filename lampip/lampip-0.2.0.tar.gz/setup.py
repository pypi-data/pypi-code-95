# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lampip', 'lampip.core']

package_data = \
{'': ['*']}

install_requires = \
['boto3', 'click', 'sh', 'termcolor', 'toml']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses']}

entry_points = \
{'console_scripts': ['lampip = lampip.entrypoint:main']}

setup_kwargs = {
    'name': 'lampip',
    'version': '0.2.0',
    'description': 'Simple CLI tool for creating custom python lambda layers',
    'long_description': '# lampip: Simple CLI tool for creating python custom lambda layers\n\n[![image](https://img.shields.io/pypi/l/lampip)](https://python.org/pypi/lampip)\n[![image](https://img.shields.io/pypi/v/lampip)](https://python.org/pypi/lampip)\n[![image](https://img.shields.io/pypi/pyversions/lampip)](https://python.org/pypi/lampip)\n[![image](https://github.com/hayashiya18/lampip/actions/workflows/pytest.yml/badge.svg)](https://github.com/hayashiya18/lampip/actions/workflows/pytest.yml)\n\n---\n\n## Features\n\n- Build Python(3.6, 3.7, 3.8)-compatible custom lambda layers using Docker and pip, and push it to AWS.\n\n- Reduce the package size using some approachs.\n  - [Byte-Compile](https://docs.python.org/3.8/library/compileall.html) (that remove source comments and docstrings).\n  - Remove `*.dist-info`.\n\n## Requirements\n\n- Python3\n- Docker\n- AWS Account\n\n## Installation\n\nYou can obtain this packages using pip.\n\n```console\n$ pip3 install lampip\n```\n\nThen you can use `lampip` command.\n\n```console\n$ lampip --help\nUsage: lampip [OPTIONS] COMMAND [ARGS]...\n\n  Simple CLI tool for creating python custom lambda layers\n\nOptions:\n  --version  Show the version and exit.\n  --help     Show this message and exit.\n\nCommands:\n  deploy  Build and push lambda layer\n  new     Create the scaffold\n\n```\n\n## Usage\n\nAt the first create the scaffold\n\n```console\n$ lampip new science\n```\n\nGo to the generated directory\n\n```console\n$ cd science\n$ ls\nlampip-config.toml  other_resources  requirements.txt\n```\n\nEdit `requirements.txt`\n\n```text\nnumpy\nscipy\npandas\n```\n\nEdit `lampip-config.toml`\n\n```toml\n[lampip]\nlayername = "science"\ndescription = "numpy, scipy, and pandas"\npyversions = ["3.6", "3.7", "3.8"]\n\n[lampip.shrink]\ncompile = true\ncompile_optimize_level = 2\nremove_dist_info = true\n\n# [lampip.shrink.plotly]\n# remove_jupyterlab_plotly = true\n# remove_data_docs = true\n```\n\nBefore you deploy the lambda layer, be sure you have AWS credentials configured.\n\n```console\n(If you do not configure AWS credentials yet, ...)\n$ aws configure\nAWS Access Key ID: ?????\nAWS Secret Acess Key: ?????\nDefault region name: ?????\n```\n\n(Option) You can switch the aws credentials using environments variables.\n\n```console\n(Case1: Using AWS CLI profile)\n$ export AWS_PROFILE="subaccount"\n\n(Case2: Using AWS access key directly)\n$ export AWS_ACCESS_KEY_ID=????\n$ export AWS_SECRET_ACCESS_KEY=?????\n$ export AWS_DEFAULT_REGION=?????\n```\n\nDeploy\n\n```console\n$ lampip deploy\nStart to make dist/science_1631253196_3.6.zip\n...\nPublish the custom layer: arn:aws:lambda:ap-northeast-1:XXXXXXXXXXXX:layer:science-py38:1\nDONE: dist/science_1631253312_3.8.zip created\n\n$ ls -lh dist\n-rw-r--r-- 1 root root 68M  9月 10 23:53 science_1631253196_3.6.zip\n-rw-r--r-- 1 root root 73M  9月 10 23:54 science_1631253254_3.7.zip\n-rw-r--r-- 1 root root 73M  9月 10 23:55 science_1631253312_3.8.zip\n\n\n(The --no-upload option suppress uploading zip files)\n$ lampip deploy --no-upload\n```\n\nThen you can check deployed layers on AWS Console.\n\n![image](./assets/lambda_console.webp)\n',
    'author': 'hayashiya18',
    'author_email': 'sei8haya@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hayashiya18/lampip',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
