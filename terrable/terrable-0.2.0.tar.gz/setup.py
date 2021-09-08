# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['terrable', 'terrable.tests', 'terrable.tests.test_utils_compare_zip_files']

package_data = \
{'': ['*'],
 'terrable.tests': ['modules/foo/*'],
 'terrable.tests.test_utils_compare_zip_files': ['scenarios/*', 'sources/*']}

install_requires = \
['boto3>=1.16.16,<2.0.0']

entry_points = \
{'console_scripts': ['terrable = terrable:main']}

setup_kwargs = {
    'name': 'terrable',
    'version': '0.2.0',
    'description': 'Manage private shared terraform modules deployed to S3.',
    'long_description': '# Terrable\n\n[![PyPI version](https://badge.fury.io/py/terrable.svg)](https://pypi.org/project/terrable/)\n[![build status](https://gitlab.com/rocket-boosters/terrable/badges/main/pipeline.svg)](https://gitlab.com/rocket-boosters/terrable/commits/main)\n[![coverage report](https://gitlab.com/rocket-boosters/terrable/badges/main/coverage.svg)](https://gitlab.com/rocket-boosters/terrable/commits/main)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-white)](https://gitlab.com/pycqa/flake8)\n[![Code style: mypy](https://img.shields.io/badge/code%20style-mypy-white)](http://mypy-lang.org/)\n[![PyPI - License](https://img.shields.io/pypi/l/terrable)](https://pypi.org/project/terrable/)\n\nTerraform private module manager that uses S3 as a backend. Includes simple versioning\nof modules to make forward migration easier. Terraform supports referencing modules\nstored in S3 as compressed files (see\n[S3 Bucket](https://www.terraform.io/docs/modules/sources.html#s3-bucket)\nfor more details). However, managing those packages is not part of Terraform itself.\nThat\'s where *terr&#8226;able* comes in. The terrable CLI allows for bundling terraform\nmodule directories into compressed files and deploying them to S3 with simple\nincremental versioning. That way modules changes can be gradually introduced in\ndependent projects as needed without causing conflicts.\n\n## Installation\n\nTerrable is available via pip:\n\n```shell script\n$ pip install terrable\n```\n\nor via poetry:\n\n```shell script\n# poetry install terrable --dev\n```\n\nOnce installed, the terrable CLI command will be available in your terminal.\n\n## Usage\n\nTerrable operates primarily on a directory that contains within it one or more module\ndirectories. For example:\n\n```\n+---modules\n|   \\---aws-lambda-function\n|           main.tf\n|           output.tf\n|           variables.tf\n|           policy.json\n|\n|   \\---aws-dynamo-db-table\n|           main.tf\n|           output.tf\n|           variables.tf\n```\n\nHere the root "modules" folder contains two modules "aws-lambda-function"\nand "aws-dynamo-db-table". To deploy these as modules via terrable to an S3 bucket\nexecute the command from the parent directory of the modules folder:\n\n```shell script\n$ terrable publish ./modules/ --bucket=<BUCKET_NAME> --profile=<AWS_PROFILE_NAME>\n```\n\nThis command will iterate through each folder inside the modules directory and publish\nany that have changed since their previous publish. Any modules found not to have\nchanged will be skipped. This can be overridden with the `--force` flag. It\'s also\npossible to publish only specific modules within that folder by including the \n`--target=aws-lambda-function` flag. This flag can be specified multiple times to\npublish a select number of specific modules for a given command.\n\nTo inspect modules, there is a list command:\n\n```\n$ terrable list <MODULE_NAME> --bucket=<BUCKET_NAME> --profile=<AWS_PROFILE_NAME>\n```\n\nThis command will print all of the versions and associated metadata for the specified\nmodule.\n',
    'author': 'Scott Ernst',
    'author_email': 'swernst@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/rocket-boosters/terrable',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
