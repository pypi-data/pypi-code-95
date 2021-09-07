# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['defectio',
 'defectio.ext.commands',
 'defectio.ext.tasks',
 'defectio.models',
 'defectio.types']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0',
 'aiohttp>=3.7.4,<4.0.0',
 'msgpack>=1.0.2,<2.0.0',
 'orjson>=3.6.3,<4.0.0',
 'ulid-py>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'defectio',
    'version': '0.1.8a0',
    'description': 'Wrapper for Revolt API',
    'long_description': '# Defectio\n\n![revolt-api](https://img.shields.io/npm/v/revolt-api?label=Revolt%20API)[![Documentation Status](https://readthedocs.org/projects/defectio/badge/?version=latest)](https://defectio.readthedocs.io/en/latest/?badge=latest)\n\n**defectio** is a direct implementation of the entire Revolt API and provides a way to authenticate and start communicating with Revolt servers. It is currently in active development so not all features are yet implemented. Similar interface to discord.py\n\n## Example Usage\n\n```python3\nimport defectio\n\nclient = defectio.Client()\n\n\n@client.event\nasync def on_ready():\n    print("We have logged in.")\n\n\n@client.event\nasync def on_message(message: defectio.Message):\n    if message.author == client.user:\n        return\n    if message.content.startswith("$hello"):\n        await message.channel.send("Hello!")\n\n\nclient.run("")\n```\n\n## Contribute\n\nJoin our server [here](https://app.revolt.chat/invite/FfbwgFDk)\n',
    'author': 'Leon Bowie',
    'author_email': 'leon@bowie-co.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Darkflame72/defectio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
