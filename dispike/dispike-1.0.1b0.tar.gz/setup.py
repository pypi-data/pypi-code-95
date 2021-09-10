# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dispike',
 'dispike.creating',
 'dispike.creating.models',
 'dispike.errors',
 'dispike.eventer_helpers',
 'dispike.followup',
 'dispike.followup.storage',
 'dispike.helper',
 'dispike.incoming',
 'dispike.incoming.attribute_helpers',
 'dispike.incoming.discord_types',
 'dispike.middlewares']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.4.0,<2.0.0',
 'async-timeout>=3.0.1,<4.0.0',
 'fastapi>=0.63.0,<0.64.0',
 'httpx>=0.16.1,<0.17.0',
 'loguru>=0.5.3,<0.6.0',
 'pydantic==1.8.2',
 'typing-extensions>=3.7.4,<4.0.0',
 'uvicorn>=0.13.2,<0.14.0']

setup_kwargs = {
    'name': 'dispike',
    'version': '1.0.1b0',
    'description': 'An independent, simple to use, powerful framework for creating interaction-based Discord bots. Powered by FastAPI',
    'long_description': '<div align="center">\n<br>\n  <h1> dispike </h1>\n  <i> ⚙️  A simple to use, powerful framework for creating stateless, independent bots using <a href="https://discord.com/developers/docs/interactions/slash-commands"> Discord Slash Commands.</a> </i>\n  <br>\n  <br>\n    <a > ⚡ Powered by <a href="https://github.com/tiangolo/fastapi"> FastAPI.</a> </a>\n  <br>\n  <br>\n  <p align="center">\n    <img src="https://codecov.io/gh/ms7m/dispike/branch/master/graph/badge.svg?token=E5AXLZDP9O">\n    <img src="https://github.com/ms7m/dispike/workflows/Test%20Dispike/badge.svg?branch=master">\n    <img src="https://img.shields.io/badge/Available%20on%20PyPi-Dispike-blue?logo=pypi&link=%22https://pypi.org/project/dispike%22">\n    <img src="https://img.shields.io/badge/dynamic/json?color=blue&label=PyPi%20Version&query=%24.info.version&url=https%3A%2F%2Fpypi.org%2Fpypi%2Fdispike%2Fjson">\n  </p>\n  <br>\n</div>\n\n\n## 📦 Installation\n\n\n**Latest stable-version**\n```\npip install dispike\n```\n\n## 📚 Learn more\n- Read documentation [here](https://dispike.ms7m.me)\n- See an example bot [here](https://github.com/ms7m/dispike-example)\n- Join our Discord Server [here](https://discord.gg/yGgRmEYjju)\n\n***\n<div align="center">\n<h2> 🧑\u200d💻 Quick Start Examples </h2>\n</div>\n\n\n### Basic\n\n```python\n\nfrom dispike import Dispike, DiscordCommand, DiscordResponse\nfrom dispike import IncomingDiscordSlashInteraction\nfrom dispike.helper import Embed\n\nbot = Dispike(...)\n\n\ncommand = DiscordCommand(\n  name="stock", description="Get the latest active stocks in the market!"\n)\n\n\n@bot.on("stock")\nasync def handle_stock_request(stockticker: str, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:\n  get_price = function(stockticker...)\n  \n  embed=Embed()\n  embed.add_field(name="Stock Price for {stockticker}.", value="Current price is {get_price}", inline=True)\n  embed.set_footer(text="Request received by {ctx.member.user.username}")\n  return DiscordResponse(embed=embed)\n\n\n\nif __name__ == "__main__":\n    bot.register(command)\n    bot.run()\n```\n\n\n### Advanced\n\n```python\nimport dispike\nfrom dispike import interactions, DiscordCommand, DiscordResponse\nfrom dispike import IncomingDiscordSlashInteraction\nfrom dispike.helper import Embed\n\n\nclass SampleGroupCollection(interactions.EventCollection):\n\n    def __init__(self):\n        self._api_key = "..."\n\n    def command_schemas(self):\n        return [\n            DiscordCommand(\n                name="lateststocks", description="Get the highest performing stocks in the market currently!"\n            ),\n            interactions.PerCommandRegistrationSettings(\n                schema=DiscordCommand(\n                    name="price",\n                    description="return ticker price for server",\n                    options=[],\n                ),\n                guild_id=11111111,\n            )\n        ]\n\n    def get_stock_information(self, stock_ticker):\n        return ...\n\n    def get_portfolio_stats(self, user_id):\n        return ...\n\n    @interactions.on("lateststocks")\n    async def latest_stocks(self, ctx: IncomingDiscordSlashInteraction) -> DiscordResponse:\n        embed = Embed()\n\n        # check user\'s porfolio by looking in the database by their discord ID\n        portfolio_stats = self.get_portfolio_stats(\n            ctx.member.user.id\n        )\n\n        embed.add_field(name="Stocks are doing good!", value=f"Current portfolio is {portfolio_stats}", inline=True)\n        embed.set_footer(text="Request received by {ctx.member.user.username}")\n        return DiscordResponse(embeds=[embed])\n\n    @interactions.on("price")\n    async def get_stock_price(self, ctx: IncomingDiscordSlashInteraction, ticker: str) -> DiscordResponse:\n        embed = Embed()\n        embed.add_field(name=f"Stock Price for 1.",\n                        value=f"Current price is {self.get_stock_information(ticker)}", inline=True)\n        embed.set_footer(text="Request received by {ctx.member.user.username}")\n        return DiscordResponse(embeds=[embed])\n\n## Inside seperate file\n\nfrom dispike import Dispike, DiscordCommand\n\nbot = Dispike(...)\n\nbot.register_collection(SampleGroupCollection(), register_command_with_discord=True)\n\nif __name__ == "__main__":\n    bot.run(port=5000)\n```\n\n## Discord API Coverage\n<details><summary>View Coverage</summary>\n<p>\n\n| API Endpoint   |      Implementation   |\n|----------|:-------------:|\n| Get Global Application Commands |  **✅ Implemented** |\n| Create Global Application Command |    **✅ Implemented**   |\n| Edit Global Application Command |  **✅ Implemented** |\n| Delete Global Application Command | **✅ Implemented** |\n| Create Guild Application Command | **✅ Implemented** |\n| Edit Guild Application Command | **✅ Implemented** |\n| Delete Guild Application Command | **✅ Implemented** |\n| Create Interaction Response | **✅ Implemented** |\n| Edit Original Interaction Response | **✅ Implemented**|\n| Delete Original Interaction Response | **✅ Implemented** |\n| Create Followup Message |**✅ Implemented** |\n| Edit Followup Message | **✅ Implemented** |\n| Delete Followup Message | **✅ Implemented** |\n| Data Models and Types | **✅ Implemented** |\n| ApplicationCommand | **✅ Implemented** |\n| ApplicationCommandOption | **✅ Implemented** |\n| ApplicationCommandOptionType | **✅ Implemented** |\n| ApplicationCommandOptionChoice | **✅ Implemented** |\n| Interaction | **✅ Implemented** |\n| Interaction Response | **✅ Implemented** |\n| Message Components | **✅ Implemented** |\n| Buttons (Message Components) | **✅ Implemented** |\n| Action Rows (Message Components) | **✅ Implemented** |\n| Message Select (Message Components) | **✅ Implemented** |\n\n</p>\n</details>\n\n## ℹ️ Notice\n\n- Python 3.6+\n- Does not speak over the discord gateway. [discord-py-slash-command is what you are looking for.](https://github.com/eunwoo1104/discord-py-slash-command). \n- You will need a server to accept connections directly from discord!\n\n\n## 🧑\u200d💻 Development\n\nHelp is wanted in mantaining this library. Please try to direct PRs to the ``dev`` branch, and use black formatting (if possible).\n\n# 🎉 Special Thanks\n- [Squidtoon99](https://github.com/Squidtoon99)\n- [marshmallow](https://github.com/mrshmllow)\n',
    'author': 'Mustafa Mohamed',
    'author_email': 'ms7mohamed@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ms7m/dispike',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
