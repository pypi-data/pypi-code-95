# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mytoyota']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.1.1,<2.0.0', 'httpx>=0.18.1,<0.19.0', 'langcodes>=3.1.0,<4.0.0']

setup_kwargs = {
    'name': 'mytoyota',
    'version': '0.6.0',
    'description': 'Python client for Toyota Connected Services.',
    'long_description': '[![GitHub Workflow Status][workflow-shield]][workflow]\n[![GitHub Release][releases-shield]][releases]\n[![GitHub Activity][commits-shield]][commits]\n\n# Toyota Connected Services Python module\n\n### [!] **This is still in beta**\n\n## Description\n\nPython 3 package to communicate with Toyota Connected Services.\nThis is an unofficial package and Toyota can change their API at any point without warning.\n\n## Installation\n\nThis package can be installed through `pip`.\n\n```text\npip install mytoyota\n```\n\n## Usage\n\n### See [Documentation](https://github.com/DurgNomis-drol/mytoyota/documentation.md)\n\n## Known issues\n\n- Statistical endpoint will return `None` if no trip have been performed in the requested timeframe. This problem will often happen at the start of each week, month or year. Also daily stats will of course also be unavailable if no trip have been performed.\n\n## Contributing\n\nThis python module uses poetry and pre-commit.\n\nTo start contributing, fork this repository and run `poetry install`. Then create a new branch. Before making a PR, please run pre-commit `poetry run pre-commit run --all-files` and make sure that all tests passes locally first.\n\n## Note\n\nAs I [@DurgNomis-drol](https://github.com/DurgNomis-drol) am not a professional programmer. I will try to maintain it as best as I can. If someone is interested in helping with this, they are more the welcome to message me to be a collaborator on this project.\n\n## Credits\n\nA huge thanks go to [@calmjm](https://github.com/calmjm) for making [tojota](https://github.com/calmjm/tojota).\n\n[releases-shield]: https://img.shields.io/github/release/DurgNomis-drol/mytoyota.svg?style=for-the-badge\n[releases]: https://github.com/DurgNomis-drol/mytoyota/releases\n[workflow-shield]: https://img.shields.io/github/workflow/status/DurgNomis-drol/mytoyota/Linting?style=for-the-badge\n[workflow]: https://github.com/DurgNomis-drol/mytoyota/actions\n[commits-shield]: https://img.shields.io/github/commit-activity/y/DurgNomis-drol/mytoyota.svg?style=for-the-badge\n[commits]: https://github.com/DurgNomis-drol/mytoyota/commits/master\n',
    'author': 'Simon Grud Hansen',
    'author_email': 'simongrud@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DurgNomis-drol/mytoyota',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
