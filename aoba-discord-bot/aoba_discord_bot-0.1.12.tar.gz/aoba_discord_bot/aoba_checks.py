from discord.ext.commands import Context


async def author_is_admin(ctx: Context) -> bool:
    return ctx.author.guild_permissions.administrator


async def author_is_not_bot(ctx: Context) -> bool:
    return not ctx.author.bot
