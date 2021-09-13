from typing import Text
from pathlib import Path
import hikari
import tanjun


"""

Tanjun bot

The 'hikari-tanjun' is a module for creating command handlers easiers.

The difference bewteen tanjun and lightbulb is that tanjun is fully slash commands.
Discord staff has stated by April 2022 All bots must use all slash commands and no prefix
Tanjun is also a more 'heavy' package

"""
# One function for creating the whole thing is way easier so all you have to do is fill in fields
# Tanjun also uses the hikari gateway bot and not their own implementation like lightbulb. Tanjun is just a command handler
# Also tanjun is made for single bot servers
def bot(token: Text, intents: hikari.Intents, guild_id: int, module_path: Path) -> hikari.GatewayBot:
    # Creates the bot instance
    bot = hikari.GatewayBot(token=token, intents=intents)

    # Since tanjun is fully modular, it has its own loading command system. This just links the bot with the tanjun client
    client = tanjun.Client.from_gateway_bot(bot, set_global_commands=guild_id)

    # Loads all the modules from the given module path
    client.load_modules(*Path(module_path).glob("*.py"))

    # Returns the bot so you can do 'bot().run()'
    return bot

    