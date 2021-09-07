# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dontuserepl', 'dontuserepl.uptimerobot']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.7.4.post0', 'aiolimiter==1.0.0b1']

setup_kwargs = {
    'name': 'dontuserepl',
    'version': '0.1.0',
    'description': 'Simple tools to deploy a script 24/7 on repl.it using an aiohttp server and automated uptimerobot monitors',
    'long_description': '# dontuserepl\n\nLet\'s face it, repl.it is one of the best places to develop, test and run code. As such, it\'s been popular for small discord bots for a couple of years now. Many people dislike the platform for various reasons, mainly, low resources, public code, etc, and they\'ll tell you to stop using it, however it remains a good place to start out and try new code easily.\n\nThe most popular way to run a discord bot on repl is to create a webserver on a different thread and configure a monitor service like uptimerobot.com to ping the server every five minutes or so.\n\nEven though this is very simple to do, i feel bored by it, that\'s why i wrote this simple library.\n\n# How to use it:\nMaking your bot 24/7 is extremely easy with `dontuserepl`.\n\n1) Go to https://uptimerobot.com/, open an account and login.\n2) Go to "My settings" and scroll to "API Settings".\n3) Create and copy a "Main API Key"\n4) Go to your repl and add the key as a secret\n5) Add the snippet below to your main.py file.\n```python\nimport os\nfrom dontuserepl import lazy_setup\nkey = os.getenv(\'uptimerobot_api_key\')  # use the name of the secret from step 4\nlazy_setup(key)\n```\n6) That\'s it, `lazy_setup` runs a minimal aiohttp server on port 8080 and configures a monitor for the script.\n\n\n# Working example\n```python\nimport os\nfrom dontuserepl import lazy_setup\nfrom discord.ext import commands\n\nkey = os.getenv(\'uptimerobot_api_key\')\ntoken = os.getenv(\'discord_token\')\n\nbot = commands.Bot(command_prefix=\'!\')\n\n@bot.even\nasync def on_ready():\n    print(f\'logged in as "{bot.user.name}"\')\n\n@bot.command()\nasync def ping(ctx):\n    await ctx.send(\'pong\')\n\n\nlazy_setup(key)\nbot.run(token)\n```\n\n# todo:\n- [ ] Upload to pypi\n- [ ] Documentations\n',
    'author': 'chrisdewa',
    'author_email': 'alexdewa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chrisdewa/dontuserepl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.5,<4.0.0',
}


setup(**setup_kwargs)
