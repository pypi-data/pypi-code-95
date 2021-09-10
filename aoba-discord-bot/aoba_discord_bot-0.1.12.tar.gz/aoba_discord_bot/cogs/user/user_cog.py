import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context, DefaultHelpCommand

from aoba_discord_bot.formatting import mention_author


class AobaHelp(DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.width = 43

    def add_indented_commands(self, commands, *, heading, max_size=None):
        if not commands:
            return

        self.paginator.add_line(heading)
        max_size = max_size or self.get_max_size(commands)

        get_width = discord.utils._string_width
        for command in commands:
            name = command.name
            width = max_size - (get_width(name) - len(name))
            ctx: Context = self.context
            bot: Bot = ctx.bot
            prefix = bot.command_prefix(None, ctx.message)
            entry = "{0}{1:<{width}} {2}".format(
                (self.indent - 1) * " " + prefix, name, command.short_doc, width=width
            )
            self.paginator.add_line(self.shorten_text(entry))
        self.paginator.add_line("")

    def shorten_text(self, text):
        if len(text) > self.width:
            start, rest = text[: self.width], text[self.width :]
            max_cmd_name_size = self.get_max_size(self.context.bot.commands)
            step = self.width - max_cmd_name_size - 3
            split_rest = [rest[i : i + step] for i in range(0, len(rest), step)]

            margin_left = " " * (max_cmd_name_size + 3)
            for i in range(len(split_rest)):
                split_rest[i] = f"{margin_left}{split_rest[i].strip()}"

            split_rest.insert(0, start)

            return "\n".join(split_rest)
        return text


class User(commands.Cog, name="User"):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = AobaHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @commands.command(aliases=["em"], help="Escapes all Markdown in the message")
    async def escape_markdown(self, ctx: Context, *messages: str):
        chars_to_escape = "*", "_", "`", ">"
        escaped_messages = list()
        for message in messages:
            escaped_messages.append(
                "".join(f"\\{ch}" if ch in chars_to_escape else ch for ch in message)
            )
        await ctx.send(f"{mention_author(ctx)}:\n{' '.join(escaped_messages)}")
