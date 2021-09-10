from discord.ext.commands import Context


def mention_author(ctx: Context) -> str:
    return f"<@{ctx.author.id}>"
