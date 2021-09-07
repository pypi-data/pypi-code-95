# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['corded', 'corded.http', 'corded.objects', 'corded.ws']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'corded',
    'version': '1.5.1',
    'description': 'A lightweight, extensible client library for Discord bots',
    'long_description': '# Corded\n\nA lightweight, extensible client library for Discord bots\n\nExample usage:\n```py\nfrom corded import CordedClient, GatewayEvent, Intents\n\n\nbot = CordedClient("my_token", Intents.default())\n\n@bot.on("message_create")\nasync def on_message_create(event: GatewayEvent) -> None:\n    data = event.typed_data\n\n    print(data["content"])\n\nbot.start()\n```\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
