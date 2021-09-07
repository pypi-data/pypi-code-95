# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tft_loaded_dice']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tft-loaded-dice',
    'version': '11.18.0',
    'description': 'Loaded dice odds for Teamfight Tactics',
    'long_description': '## tft-loaded-dice\n[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/stradivari96/tft-loaded-dice/blob/master/LICENSE)\n[![codecov](https://codecov.io/gh/stradivari96/tft-loaded-dice/branch/main/graph/badge.svg?token=NYKUYQR8ZG)](https://codecov.io/gh/stradivari96/tft-loaded-dice)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Usage\n```python\nfrom tft_loaded_dice import best_champions, champion_odds\n\nbest_champions("Gwen", level=7)\n# [(\'Gwen\', 0.0196078431372549), (\'Lux\', 0.005), (\'Lulu\', 0.005), (\'Fiddlesticks\', 0.005)]\n\nchampion_odds("Nocturne")\n# {\'Nocturne\': {3: 0.0, 4: 0.15, 5: 0.2, 6: 0.3, 7: 0.35, 8: 0.35, 9: 0.3}, \'Fiddlesticks\': {3: 0.0, 4: 0.0375, 5: 0.05, 6: 0.075, 7: 0.0875, 8: 0.0875, 9: 0.075}, \'Volibear\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15}, \'Pyke\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15}, \'Viego\': {3: 0.0, 4: 0.0375, 5: 0.05, 6: 0.075, 7: 0.0875, 8: 0.0875, 9: 0.075}, \'Diana\': {3: 0.0, 4: 0.05, 5: 0.06666666666666667, 6: 0.1, 7: 0.11666666666666665, 8: 0.11666666666666665, 9: 0.1}, "Kha\'Zix": {3: 0.0, 4: 0.05, 5: 0.06666666666666667, 6: 0.1, 7: 0.11666666666666665, 8: 0.11666666666666665, 9: 0.1}, \'Ivern\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15}}\n\n```\n\n## References\n* https://github.com/alanz132/loadedDiceOdds\n* https://giantslayer.tv/blogs/5261054387/correctly-using-loaded-dice/\n* https://www.reddit.com/r/CompetitiveTFT/comments/kw4ah7/loaded_die_odds_for_every_champion/\n\n## Development\n\n1. Install poetry\n\nhttps://python-poetry.org/docs/#installation\n\n2. Install dependencies\n```\npoetry install\npoetry run pre-commit install\n```\n\n3. Run test\n```\npoetry run pytest --cov=tft_loaded_dice --cov-fail-under=80 --cov-report xml\n```\n\n* Gitmoji: https://gitmoji.dev/\n* Black: https://black.readthedocs.io/en/stable/\n* Isort: https://pycqa.github.io/isort/\n* Poetry: https://python-poetry.org/',
    'author': 'Xiang Chen',
    'author_email': 'xiangchenchen96@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stradivari96/tft-loaded-dice',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
