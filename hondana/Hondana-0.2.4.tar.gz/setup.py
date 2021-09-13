# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hondana', 'hondana.types']

package_data = \
{'': ['*'], 'hondana': ['extras/*']}

modules = \
['py', 'tags']
install_requires = \
['aiohttp>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['version = hondana.__main__:show_version']}

setup_kwargs = {
    'name': 'hondana',
    'version': '0.2.4',
    'description': 'An asynchronous wrapper around the MangaDex v5 API',
    'long_description': '<div align="center">\n    <h1><a href="https://jisho.org/word/%E6%9C%AC%E6%A3%9A">Hondana 『本棚』</h1>\n    <a href=\'https://hondana.readthedocs.io/en/latest/?badge=latest\'>\n        <img src=\'https://readthedocs.org/projects/hondana/badge/?version=latest\' alt=\'Documentation Status\' />\n    </a>\n    <a href=\'https://github.com/AbstractUmbra/Hondana/actions/workflows/build.yaml\'>\n        <img src=\'https://github.com/AbstractUmbra/Hondana/workflows/Build/badge.svg\' alt=\'Build status\' />\n    </a>\n    <a href=\'https://github.com/AbstractUmbra/Hondana/actions/workflows/lint.yaml\'>\n        <img src=\'https://github.com/AbstractUmbra/Hondana/workflows/Lint/badge.svg\' alt=\'Build status\' />\n    </a>\n</div>\n<div align="center">\n    <a href=\'https://api.mangadex.org/\'>\n        <img src=\'https://img.shields.io/website?down_color=red&down_message=offline&label=API%20Status&logo=MangaDex%20API&up_color=lime&up_message=online&url=https%3A%2F%2Fapi.mangadex.org%2Fping\' alt=\'API Status\'/>\n    </a>\n</div>\n<br>\n\nA lightweight and asynchronous wrapper around the [MangaDex v5 API](https://api.mangadex.org/docs.html).\n\n## Features\n**NOTE** This library is still in development, I will list off the API methods and their progress here:\n\n| Feature          | Implemented? | Notes                                                                |\n| ---------------- | ------------ | -------------------------------------------------------------------- |\n| Chapter Upload   | [ ]          | Soon:tm:                                                             |\n| Manga            | [x]          | Done.                                                                |\n| Cover            | [x]          | Done.                                                                |\n| Author           | [x]          | Done.                                                                |\n| Search           | [x]          | Done.                                                                |\n| Auth             | [x]          | Authentication is done per request, token handled.                   |\n| Scanlation Group | [x]          | Done.                                                                |\n| Feed             | [x]          | Done                                                                 |\n| CustomList       | [x]          | Done.                                                                |\n| AtHome           | [x]          | Done.                                                                |\n| Legacy           | [x]          | Done.                                                                |\n| Infrastructure   | [x]          | Done.                                                                |\n| Upload           | [ ]          | Soon:tm:                                                             |\n| Account          | [x]          | Done.                                                                |\n| User             | [x]          | Done.                                                                |\n| Chapter          | [x]          | Done.                                                                |\n| Report           | [x]          | Done.                                                                |\n| Ratelimits?      | [x]          | Ratelimits are handled per HTTP request following the standard flow. |\n\n\n## Note about authentication\nSadly (thankfully?) I am not an author on MangaDex, meaning I cannot test the creation endpoints for things like scanlators, artists, authors, manga or chapters.\nI have followed the API guidelines to the letter for these, but they may not work.\n\nAny help in testing them is greatly appreciated.\n\n## Note about upload/creation\nFollowing the above, this means I also cannot test manga creation or chapter creation/upload.\nThese are currently a WIP.\n\n## Examples\nPlease take a look at the [examples](./examples/) directory for working examples.\n\n**NOTE**: More examples will follow as the library is developed.\n\n### API caveats to note\n\n- There are no API endpoints for Artist. It seems they are not differentiated from Author types except in name only.\n- The tags are locally cached since you **must** pass UUIDs to the api (and I do not think you\'re going to memorise those), there\'s a convenience method for updating the local cache as `Client.update_tags`\n  - I have added [an example](./examples/updating_local_tags.py) on how to do the above.\n',
    'author': 'Alex Nørgaard',
    'author_email': 'Umbra@AbstractUmbra.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AbstractUmbra/hondana',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
