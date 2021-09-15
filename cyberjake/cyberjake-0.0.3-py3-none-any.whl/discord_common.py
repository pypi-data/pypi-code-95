"""Common code for discord bots"""
import random
import typing

# Used to all for no discord uses of common
try:
    import discord

    DISCORD_PRESENT = True
except ModuleNotFoundError:
    DISCORD_PRESENT = False


async def error_embed(ctx, message: str, title: str = "Error:", **kwargs):
    """
    Makes and send an error embed

    **Requires discord.py**

    **Asynchronous Function**

    :raises ModuleNotFoundError: Will raise a ModuleNotFoundError if discord.py module \
    is not installed

    :param ctx: Command context
    :type ctx: discord.ext.commands.Context
    :param message: Message description
    :type message: str
    :param title: Error message title
    :type title: str
    """
    if not DISCORD_PRESENT:
        raise ModuleNotFoundError("Need discord.py module installed")
    await make_embed(ctx, color="FF0000", send=True, description=message, title=title, **kwargs)


async def make_embed(
    ctx, color: typing.Union[str, int] = None, send: typing.Union[bool, str] = True, **kwargs
) -> typing.Optional["discord.Embed"]:
    """
    Makes and defaults to sending a discord.Embed

    **Requires discord.py**

    **Asynchronous Function**

    :raises ModuleNotFoundError: Will raise a ModuleNotFoundError if discord.py module \
    is not installed

    :param ctx: Discord context
    :type ctx: discord.ext.commands.Context
    :param color: Color of the embed
    :type color: [str, int]
    :param send: Send the message instead of returning
    :type send: bool
    :param kwargs: Keyword arguments to pass to embed
    :return: Filled out embed if send is False
    """
    if not DISCORD_PRESENT:
        raise ModuleNotFoundError("Need discord.py module installed")
    if not color:
        kwargs["color"] = int("0x%06x" % random.randint(0, 0xFFFFFF), 16)  # nosec
    elif isinstance(color, str):
        kwargs["color"] = discord.Color(int(color, 16))

    embed = discord.Embed(timestamp=ctx.message.created_at, **kwargs)

    if "footer" in kwargs:
        embed.set_footer(text=kwargs["footer"])
    if send:
        await ctx.send(embed=embed)
    else:
        return embed
