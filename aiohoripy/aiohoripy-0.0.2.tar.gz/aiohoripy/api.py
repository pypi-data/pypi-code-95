from .http import *
sfw_tags = ["all", "husbando", "waifu"]
nsfw_tags = ["ass", "ecchi", "ero", "hentai", "maid", "milf", "oppai", "oral", "paizuri", "selfies", "uniform"]
async def sfw(tag):
    if tag in sfw_tags:
        session = await session_json(F"https://api.hori.ovh/sfw/{tag}/")
        return session
    print(F"There is no {tag} tag\nConsider using:\n{sfw_tags} tags")

async def nsfw(tag):
    if tag in nsfw_tags:
        session = await session_json(F"https://api.hori.ovh/nsfw/{tag}/")
        return session
    print(F"There is no {tag} tag\nConsider using:\n{nsfw_tags} tags")
