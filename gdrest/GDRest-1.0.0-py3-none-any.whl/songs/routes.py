from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Mount, Route

from auth import auth_client
from gdrest.songs.song import Song


async def get_song(request: Request):
    client = auth_client(request.user)
    sid: int = request.path_params["sid"]
    so = await client.get_song(sid)
    song = Song.from_song_object(so)
    return JSONResponse(dict(song))


async def listen_song(request: Request):
    client = auth_client(request.user)
    sid: int = request.path_params["sid"]
    so = await client.get_song(sid)
    song = Song.from_song_object(so)
    return StreamingResponse(song.audio, media_type='audio/mpeg')


SongMount = Mount("/song", routes=[
    Route("/{sid:int}", get_song),
    Route("/{sid:int}/listen", listen_song)
])
