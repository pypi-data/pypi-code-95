import fastapi

from starlette.exceptions import HTTPException as StarletteHTTPException

from gaea.database import db
from gaea.log import logger


def get_session(request: fastapi.Request):
    return request.state.session


class MiddleWare:
    def __init__(self, db_client=None):
        self.db = db_client

    async def before_request(self, *args, **kwargs):
        pass

    async def after_request(self, *args, **kwargs):
        pass

    async def exception_handler(self, *args, **kwargs):
        pass

    async def __call__(self, request: fastapi.Request, call_next):
        await self.before_request()

        if self.db:
            session = self.db.get_session()
            request.state.session = session

        try:
            response = await call_next(request)

        except:
            await self.exception_handler()
            logger.exception("Unexpected exception happened")
            response = fastapi.Response(
                status_code=500, content="Unexpected error happened"
            )

        finally:

            if self.db:
                session.close()

            await self.after_request()

        return response
