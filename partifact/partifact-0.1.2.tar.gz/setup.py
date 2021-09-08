# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['partifact']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15,<2.0',
 'parse>=1.19.0,<2.0.0',
 'tomlkit>=0.7.0,<1.0.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['partifact = partifact.main:app']}

setup_kwargs = {
    'name': 'partifact',
    'version': '0.1.2',
    'description': '',
    'long_description': '# partifact\n\npartifact is a tool to help with configuring and authenticating CodeArtifact as a repository for [Poetry](https://github.com/python-poetry/poetry) and [pip](https://pip.pypa.io/en/stable/).\n\n[AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/codeartifact/login.html) offers functionality to configure CodeArtifact for pip.\nThis tool offers the following improvements over the CLI:\n1. Poetry support.\n1. Assuming an AWS role to get the token. This is handy in automated pipelines, which may have the access key and secret key as environment variables,\n  but want to install packages from CodeArtifact on a different account.\n1. Configuration persisted in a config file, making the tool more convenient to use than the CLI with the options it requires to be passed in from the command line.\n\n\n# How to use?\n\nInstall partifact from pypi using pip the usual way:\n\n```shell\npip install partifact\n```\n\nIt\'s best to do this globally, rather than inside the virtualenv.\n\nBefore you can use partifact, the Poetry source repository needs to be\n[configured](https://python-poetry.org/docs/pyproject/#dependencies-and-dev-dependencies)\nin `pyproject.toml`.\n\n```toml\n[[tool.poetry.source]]\nname = "my-repo"\nurl = "https://{code_artifact_domain}-{aws_account}.d.codeartifact.{aws_region}.amazonaws.com/pypi/{code_artifact_repository}/simple/"\ndefault = true  # if this should be the default repository to install from\n```\n\nOnce Poetry is configured, you can use the partifact command to authenticate:\n\n```shell\npartifact login my-repo\n```\n\n> **NOTE**: Make sure your run the command from the directory where your `pyproject.toml` is!\n\n\nOptionally, you can pass in an AWS profile and/or AWS role to use\nfor CodeArtifact token generation.\n\n```shell\npartifact login myrepo --profile myprofile\npartifact login myrepo --role myrole\n```\n',
    'author': 'David Steiner',
    'author_email': 'david_j_steiner@yahoo.co.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Validus-Risk-Management/partifact',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
