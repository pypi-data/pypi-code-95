# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['djlint', 'djlint.formatter']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'regex>=2021.8.28,<2022.0.0',
 'tomlkit>=0.7.2,<0.8.0',
 'tqdm>=4.62.2,<5.0.0']

extras_require = \
{'test': ['coverage>=5.5,<6.0',
          'pytest>=6.2.5,<7.0.0',
          'pytest-cov>=2.12.1,<3.0.0']}

entry_points = \
{'console_scripts': ['djlint = djlint:main']}

setup_kwargs = {
    'name': 'djlint',
    'version': '0.3.8',
    'description': 'HTML Template Linter and Formatter',
    'long_description': '![djLint Logo](https://raw.githubusercontent.com/Riverside-Healthcare/djlint/master/docs/_static/icon.png)\n\nFind common formatting issues and *reformat* HTML templates.\n\n***Django\u2003·\u2003Jinja\u2003·\u2003Nunjucks\u2003·\u2003Handlebars***\n\nPs, ``--check`` it out on other templates as well!\n\n[![codecov](https://codecov.io/gh/Riverside-Healthcare/djlint/branch/master/graph/badge.svg?token=eNTG721BAA)](https://codecov.io/gh/Riverside-Healthcare/djlint) [![test](https://github.com/Riverside-Healthcare/djlint/actions/workflows/test.yml/badge.svg)](https://github.com/Riverside-Healthcare/djlint/actions/workflows/test.yml) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/dba6338b0e7a4de896b45b382574f369)](https://www.codacy.com/gh/Riverside-Healthcare/djlint/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Riverside-Healthcare/djlint&amp;utm_campaign=Badge_Grade) [![Maintainability](https://api.codeclimate.com/v1/badges/5febe4111a36c7e0d2ed/maintainability)](https://codeclimate.com/github/Riverside-Healthcare/djlint/maintainability) [![Downloads](https://pepy.tech/badge/djlint)](https://pepy.tech/project/djlint)[![chat](https://img.shields.io/badge/chat-discord-green)](https://discord.gg/taghAqebzU)\n\n## Documentation\n\nRead the [documentation](https://djlint.readthedocs.io)\n\n## Installation and Usage\n\n**djLint** can be installed with `pip install djlint`, and is easy to run:\n\n```sh\n# to lint a directory\ndjlint /path\n\n# to lint a directory with custom extension\ndjlint /path -e html.dj\n\n# to check formatting on a file\ndjlint /path/file.html.j2 --check\n\n# to reformt a directory without printing the file diff\ndjlint /path --reformat --quiet\n\n# using stdin\necho "<div></div>" | djlint -\n\n```\n\n## Show your format\n\nAdd a badge to your projects ```readme.md```:\n\n```md\n[![Code style: djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://github.com/Riverside-Healthcare/djlint)\n```\n\nAdd a badge to your ```readme.rst```:\n\n```rst\n.. image:: https://img.shields.io/badge/html%20style-djlint-blue.svg\n   :target: https://github.com/Riverside-Healthcare/djlint\n```\nLooks like this:\n\n[![djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://github.com/Riverside-Healthcare/djlint)\n\n\n## Contributing\n\nCheckout the [issue](https://github.com/Riverside-Healthcare/djlint/issues) list and help where you can.\n',
    'author': 'Christopher Pickering',
    'author_email': 'cpickering@rhc.net',
    'maintainer': 'Christopher Pickering',
    'maintainer_email': 'cpickering@rhc.net',
    'url': 'https://github.com/Riverside-Healthcare/djlint',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
