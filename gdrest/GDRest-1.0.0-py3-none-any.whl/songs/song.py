import io

import gd
import typesystem
import httpx

class Song(typesystem.Schema):
    name = typesystem.String()
    author = typesystem.String()
    id = typesystem.Integer()
    scope = typesystem.Choice(choices=["official", "custom"])
    link = typesystem.String(allow_null=True)
    download_link = typesystem.String(allow_null=True)

    @classmethod
    def from_song_object(cls, song: gd.Song):
        data = {
            "name": song.name,
            "author": song.author,
            "id": song.id,
            "scope": "custom" if song.is_custom() else "official",
            "link": song.link,
            "download_link": song.download_link
        }
        return cls.validate(data)

    @classmethod
    def from_level(cls, lvl: gd.Level):
        return cls.from_song_object(lvl.song)

    @property
    def audio(self):
        au = httpx.get(self.download_link)
        return io.BytesIO(au.content)
