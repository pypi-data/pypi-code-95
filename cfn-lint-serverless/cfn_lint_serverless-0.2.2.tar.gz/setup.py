# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cfn_lint_serverless', 'cfn_lint_serverless.rules']

package_data = \
{'': ['*']}

install_requires = \
['cfn-lint>=0.49.2,<0.55.0']

setup_kwargs = {
    'name': 'cfn-lint-serverless',
    'version': '0.2.2',
    'description': 'Serverless rules for cfn-lint',
    'long_description': 'cfn-lint-serverless\n===================\n\nRuleset for [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) for serverless applications.\n\nInstallation\n------------\n\n```bash\npip install cfn-lint cfn-lint-serverless\n```\n\nUsage\n-----\n\n```bash\ncfn-lint template.yaml -a cfn_lint_serverless.rules\n```',
    'author': 'Amazon Web Services',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
