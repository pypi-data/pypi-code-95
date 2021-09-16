import gd
from starlette.requests import Request
from starlette.responses import JSONResponse

from gdrest.levels.level import Level
from auth import auth_client


async def search_levels(request: Request):
    client = auth_client(request.user)
    query: str = request.path_params["query"]
    lvls: list[gd.Level] = await client.search_levels(query)
    display = {"levels": [dict(Level.from_lvl_object(lvl)) for lvl in lvls]}
    return JSONResponse(display)