import gd
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Mount, Route

from gdrest.levels.level import Level
from auth import auth_client


async def get_level(request: Request):
    client = auth_client(request.user)
    lid: int = request.path_params["lid"]
    try:
        lvl = await client.get_level(lid)
    except gd.MissingAccess:
        return JSONResponse({
            "title": "Level not found",
            "message": "Either the servers are down, or the level was not found in the servers"
        }, status_code=404)
    info = Level.from_lvl_object(lvl)
    return JSONResponse(dict(info))


async def listen_level_song(request: Request):
    client = auth_client(request.user)
    lid: int = request.path_params["lid"]
    try:
        lvl = await client.get_level(lid)
    except gd.MissingAccess:
        return JSONResponse({
            "title": "Level not found",
            "message": "Either the servers are down, or the level was not found in the servers"
        }, status_code=404)
    song_id = lvl.song.id
    return RedirectResponse(f"/song/{song_id}/listen")


LevelMount = Mount("/level", routes=[
    Route("/{lid:int}", get_level),
    Route("/{lid:int}/listen", listen_level_song)
])
