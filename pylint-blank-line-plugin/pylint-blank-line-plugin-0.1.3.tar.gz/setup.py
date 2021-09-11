# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylint_blank_line_plugin']

package_data = \
{'': ['*']}

install_requires = \
['pylint']

setup_kwargs = {
    'name': 'pylint-blank-line-plugin',
    'version': '0.1.3',
    'description': 'Plugin for pylint which checks blank line before and after return, yield, raise, break, continue statements  ',
    'long_description': '## Plugin for pylint which checks blank line before and after return, yield, raise, break, continue statements\n\nInstall:\n```bash\npip install pylint-blank-line-plugin\n```\n\nUsage:\n```bash\npylint --load-plugins blank_line FILES_TO_CHECK\n```\n',
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
