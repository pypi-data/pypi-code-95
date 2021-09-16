import gd
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.authentication import requires
from starlette.status import HTTP_401_UNAUTHORIZED as UNAUTHORIZED

from auth import auth_client


@requires("authenticated", status_code=UNAUTHORIZED)
async def comment(request: Request):
    client = auth_client(request.user)
    lid: int = request.path_params["lid"]
    lvl = await client.get_level(lid)
    content: str = await request.json()["content"]
    await lvl.comment(content)