"""Main module."""
import discord
from discord.ext.commands import Bot, Command, Context
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session

from aoba_discord_bot.cogs.admin import Admin
from aoba_discord_bot.cogs.bot_admin import BotAdmin
from aoba_discord_bot.cogs.osu import Osu
from aoba_discord_bot.cogs.user import User
from aoba_discord_bot.db_models import AobaCommand, AobaGuild


class AobaDiscordBot(Bot):
    def __init__(self, aoba_params: dict, **options):
        super().__init__(**options)
        self.db_session: Session = aoba_params.get("db_session")
        self.add_cog(Admin(self, self.db_session))
        self.add_cog(BotAdmin(self, self.db_session))
        self.add_cog(User(self))
        self.add_cog(
            Osu(
                client_id=aoba_params.get("osu_client_id"),
                client_secret=aoba_params.get("osu_client_secret"),
            )
        )

        @self.check
        async def globally_block_dms(ctx: Context):
            return ctx.guild is not None

        @self.event
        async def on_ready():
            async def insert_new_guilds_in_db():
                bot_guild_ids = {guild.id for guild in self.guilds}
                persisted_guild_ids = {
                    guild.guild_id for guild in self.db_session.query(AobaGuild)
                }
                new_guilds = bot_guild_ids.difference(persisted_guild_ids)
                for new_guild_id in new_guilds:
                    new_guild = AobaGuild(guild_id=new_guild_id, command_prefix="!")
                    print(f" - Added database record for guild `{new_guild_id}`")
                    self.db_session.add(new_guild)
                if len(new_guilds) > 0:
                    self.db_session.commit()
                    print(f"{len(new_guilds)} guilds added the bot since the last run")

            async def add_persisted_custom_commands():
                async def custom_command(ctx: Context):
                    try:
                        custom_cmd = (
                            self.db_session.query(AobaCommand)
                            .filter(AobaCommand.name == ctx.command.name)
                            .one()
                        )
                        await ctx.channel.send(custom_cmd.text)
                    except (NoResultFound, MultipleResultsFound) as e:
                        await ctx.channel.send(
                            "Error trying to get command record, check the logs for more information"
                        )
                        print(e)

                for command in self.db_session.query(AobaCommand):
                    self.add_command(Command(custom_command, name=command.name))

            print(f"Logged on as {self.user}")
            await insert_new_guilds_in_db()
            await add_persisted_custom_commands()
            await self.change_presence(
                status=discord.Status.online, activity=discord.Game("in the cloud")
            )
