from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from auth import GDAuthBackend
import uvicorn

from gdrest.levels.routes import LevelMount
from gdrest.users.routes import UserMount
from gdrest.me.routes import MyMount
from gdrest.songs.routes import SongMount

routes = [LevelMount, UserMount, MyMount, SongMount]
middleware = [
    Middleware(AuthenticationMiddleware, backend=GDAuthBackend())
]
app = Starlette(routes=routes,middleware=middleware)
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=4700)
