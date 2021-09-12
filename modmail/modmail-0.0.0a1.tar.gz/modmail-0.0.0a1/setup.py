# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modmail']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'modmail',
    'version': '0.0.0a1',
    'description': 'A modmail bot for Discord. Python 3.8+ compatible.',
    'long_description': '# modmail\n\n[![Lint & Test](https://img.shields.io/github/workflow/status/discord-modmail/modmail/Lint%20&%20Test/main?label=Lint+%26+Test&logo=github&style=flat)](https://github.com/discord-modmail/modmail/actions/workflows/lint_test.yml "Lint and Test")\n[![Code Coverage](https://img.shields.io/codecov/c/gh/discord-modmail/modmail/main?logo=codecov&style=flat&label=Code+Coverage)](https://app.codecov.io/gh/discord-modmail/modmail "Code Coverage")\n[![Codacy Grade](https://img.shields.io/codacy/grade/78be21a49835484595aea556d5920638?logo=codacy&style=flat&label=Code+Quality)](https://www.codacy.com/gh/discord-modmail/modmail/dashboard "Codacy Grade")\n[![Python](https://img.shields.io/static/v1?label=Python&message=3.8+%7C+3.9&color=blue&logo=Python&style=flat)](https://www.python.org/downloads/ "Python 3.8 | 3.9")\n[![License](https://img.shields.io/github/license/discord-modmail/modmail?style=flat&label=License)](./LICENSE "License file")\n[![Code Style](https://img.shields.io/static/v1?label=Code%20Style&message=black&color=000000&style=flat)](https://github.com/psf/black "The uncompromising python formatter")\n\nAn MIT licensed modmail bot for Discord.\n',
    'author': 'onerandomusername',
    'author_email': 'genericusername414@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://discord-modmail.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
