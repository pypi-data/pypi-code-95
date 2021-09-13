from typing import Text
import hikari
import lightbulb
import os

"""

Lightbulb bot

The 'hikari-lightbulb' is a module for creating bots

Lighbulb has its own bot implementation and no custom command handler.
For now, lighbulb has prefixs but they will remove it by April 2022 Because of discord staff wanting fully slash commands.
Lightbulb is a 'lighter' package

"""

# One function for creating the whole thing is way easier so all you have to do is fill in fields
# Lightbulb has is their own bot with alot of extra fields to make development better than the GatewayBot from hikari
def bot(token: Text, prefix: Text, intents: hikari.Intents, sensitive: bool) -> lightbulb.Bot:
    # Creates a new bot with all the configuration given by the user
    bot = lightbulb.Bot(token=token, prefix=prefix, intents=intents, insensitive_commands=sensitive)

    # Loads all of the extensions in the command path
    # No special commmand loading from lightbulb
    for ext in os.listdir("./commands"):
        if ext.endswith(".py"):
            bot.load_extension(f"commands.{ext[:-3]}")

    # Returns the bot so you can do 'bot().run()'
    return bot