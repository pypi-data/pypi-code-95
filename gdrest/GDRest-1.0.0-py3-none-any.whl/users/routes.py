import gd
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Mount, Route

from gdrest.users.user import User
from auth import auth_client
from gdrest.levels.level import Level


async def get_user(request: Request):
    client = auth_client(request.user)
    username: str = request.path_params["username"]
    try:
        user = await client.search_user(username)
    except gd.MissingAccess:
        return PlainTextResponse("Nothing found", status_code=404)
    info = User.from_user_object(user)
    return JSONResponse(dict(info))


async def get_levels(request: Request):
    client = auth_client(request.user)
    username: str = request.path_params["username"]
    user = await client.search_user(username)
    lvls: list[gd.Level] = await user.get_levels()
    display = {
        'levels': []
    }
    for lvl in lvls:
        display['levels'].append(dict(Level.from_lvl_object(lvl)))
    return JSONResponse(display)


async def get_posts(request: Request):
    client = auth_client(request.user)
    username: str = request.path_params["username"]
    user = await client.search_user(username)
    posts: list[gd.Comment] = await user.get_profile_comments()
    display = dict(posts=[dict(content=p.content) for p in posts])
    return JSONResponse(display)


UserMount = Mount("/user", routes=[
    Route("/{username:str}", get_user, methods=["GET"]),
    Route("/{username:str}/levels", get_levels),
    Route("/{username:str}/posts", get_posts)
]);

