import gd
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.authentication import requires

from gdrest.users.user import User
from auth import auth_client


@requires("authenticated")
async def get_my_profile(request: Request):
    client = auth_client(request.user)
    me = await client.user.get_user()
    info = User.from_user_object(me)
    return JSONResponse(dict(info))


@requires("authenticated", status_code=404)
async def get_messages(request: Request):
    client = auth_client(request.user)
    msgs: list[gd.Message] = await client.get_messages()
    display = {"messages": []}
    if len(msgs) == 0:
        return JSONResponse({
            "title": "Yoohoo!",
            "content": "You have no messages"})
    for msg in msgs:
        await msg.read()
        display["messages"].append({
            "author": msg.author.name,
            "content": msg.content
        })
    return JSONResponse(display)


MyMount = Mount("/me", routes=[
    Route("/profile", get_my_profile, methods=["GET"]),
    Route("/mailbox", get_messages)
])
