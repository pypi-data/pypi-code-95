# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylint_exception_var_name_plugin']

package_data = \
{'': ['*']}

install_requires = \
['pylint']

setup_kwargs = {
    'name': 'pylint-exception-var-name-plugin',
    'version': '0.1.2',
    'description': 'Plugin for pylint which allows to define and check variable name for exception',
    'long_description': '## Plugin for pylint which allows defining and checking variable name for exception (like `e` or `exc` or other)\n\nInstall:\n```bash\npip install pylint-exception-var-name-plugin\n```\n\nUsage:\n```bash\npylint --load-plugins exception_var_name FILES_TO_CHECK\n```\n\n`ALLOWED_VAR_NAME` default is `e`. Can be set in command line:\n```bash\npylint --load-plugins exception_var_name ALLOWED_VAR_NAME FILES_TO_CHECK\n```\nor in pylint config file (`pylintrc`)\n```bash\nexception-var-name=ALLOWED_VAR_NAME\n```',
    'author': 'Konstantin Shestakov',
    'author_email': 'winmasta@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/winmasta',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
