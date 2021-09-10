from typing import List

import discord
from discord import Guild, Member, TextChannel
from discord.ext import commands
from discord.ext.commands import Bot, Context
from sqlalchemy.orm import Session


class BotAdmin(
    commands.Cog,
    name="BotAdmin",
):
    def __init__(self, bot: Bot, db_session: Session):
        self.bot = bot
        self.db_session = db_session

    @commands.is_owner()
    @commands.command(help="Shutdown the bot")
    async def shutdown(self, ctx: Context):
        await ctx.channel.send("Shutting down, bye admin!")
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.close()

    @commands.is_owner()
    @commands.command(
        name="guilds", aliases=["servers"], help="List of servers running Aoba"
    )
    async def get_guilds(self, ctx: Context):
        guilds_list_str = ", ".join([guild.name for guild in self.bot.guilds])
        await ctx.channel.send(f"**Guilds:**\n > {guilds_list_str}")

    @commands.is_owner()
    @commands.command(help="Change Aoba's status text")
    async def status(self, ctx: Context, *texts: str):
        if not texts:
            member: Member = None
            for guild in self.bot.guilds:
                member = guild.get_member(self.bot.user.id)
                if member:
                    break
            if member:
                await ctx.send(member.activity)
            return

        status = " ".join(texts)
        await self.bot.change_presence(activity=discord.Game(status))
        await ctx.send(f"My status was changed to `{status}`!")

    @commands.is_owner()
    @commands.command(help="(UNTESTED)Make an announcement in every server")
    async def announce(self, ctx: Context, *texts: str):
        text = " ".join(texts)

        await ctx.send(f"Announcing `{text}` in {len(self.bot.guilds)} servers.")

        announcement_channels: List[TextChannel] = list()
        guilds_with_no_announcement_channel: List[str] = list()

        for guild in self.bot.guilds:
            guild: Guild
            announcement_channel: TextChannel = None

            for channel in guild.text_channels:
                if channel.is_news():
                    announcement_channel = channel
                    break

            if not announcement_channel:
                guilds_with_no_announcement_channel.append(guild.name)
                continue

            announcement_channels.append(announcement_channel)

        if guilds_with_no_announcement_channel:
            channels = ", ".join(guilds_with_no_announcement_channel)
            await ctx.send(
                f"Announcement channel was not found for guilds:\n > {channels}"
            )

        for channel in announcement_channels:
            await channel.send(text)
