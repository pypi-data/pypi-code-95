import io
import re
from datetime import datetime, timedelta

import discord
import requests
from discord import Message
from discord.ext import commands
from discord.ext.commands import Context


class Osu(commands.Cog, name="Osu"):
    API_BASE_URL = "https://osu.ppy.sh/api/v2/"
    API_OAUTH_URL = "https://osu.ppy.sh/oauth/token"

    def __init__(self, client_id: int, client_secret: str):
        """
        The osu! API requires the client id and a secret to request a token, both of which should be passed as arguments
        running the bot to use the osu! cog. Access your osu account settings at
        https://osu.ppy.sh/home/account/edit#oauth to get the id and secret.
        """
        self.client_id, self.client_secret = client_id, client_secret
        self._access_token_info = None
        self._token_expires_dt = None

    def _get_authorization_header(self) -> dict:
        """
        Handles the request for OAuth token and re-requesting it when expired.
        return: dictionary with the authorization header with a valid OAuth token
        """
        now = datetime.now()

        def token_expired() -> bool:
            return self._token_expires_dt is not None and now >= self._token_expires_dt

        if self._access_token_info is None or token_expired():
            self._access_token_info = self._client_credentials_grant()
            secs_to_expire = int(self._access_token_info.get("expires_in"))
            self._token_expires_dt = now + timedelta(seconds=secs_to_expire)

        access_token = self._access_token_info.get("access_token")

        return {"Authorization": f"Bearer {access_token}"}

    def _client_credentials_grant(self) -> dict:
        """
        Sends a post request for a new client credential token.
        return: Dictionary with token_type(str=Bearer), expires_in(int in seconds), access_token(str)
        """
        body = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "public",
        }
        return requests.post(url=Osu.API_OAUTH_URL, data=body).json()

    @commands.command(help="Performance points obtained by the user in this map")
    async def score_pp(self, ctx: Context, beatmap_id: int, user_id: int):
        url = f"{self.API_BASE_URL}beatmaps/{beatmap_id}/scores/users/{user_id}"
        body = {
            "mode": "std",
            # "mods": "",
        }
        response = requests.get(
            url=url, data=body, headers=self._get_authorization_header()
        ).json()
        pp = response.get("score").get("pp")
        username = response.get("score").get("user").get("username")
        await ctx.send(
            content=f"** {username} ** has a **{round(pp)}pp** score on this map!"
        )

    @commands.command(
        help="Generates a backup with download links to your beatmaps by reading an attachment with your osu!.db file"
    )
    async def beatmaps_backup(self, ctx: Context):
        msg: Message = ctx.message
        file = next(iter(msg.attachments))
        contents_bin = io.BytesIO(await file.read()).getvalue()
        beatmapset_ids = [
            "".join([chr(c) for c in match[3:]])
            for match in re.findall(b"\x00\x0b.\d+ ", contents_bin)
        ]
        ids_set = set(beatmapset_ids)
        download_urls = "\n".join(
            [
                f"https://api.chimu.moe/v1/download/{bmp_set_id.strip()}?n=1"
                for bmp_set_id in ids_set
            ]
        )
        file = discord.File(io.StringIO(download_urls), filename="beatmap_dl_links.txt")
        found = (
            f"Found `{len(ids_set)}` beatmapsets for `{len(beatmapset_ids)}` beatmaps! Import the attached file"
            f" with DownThemAll! to re-download your maps."
        )
        await ctx.send(
            content=found,
            file=file,
        )
