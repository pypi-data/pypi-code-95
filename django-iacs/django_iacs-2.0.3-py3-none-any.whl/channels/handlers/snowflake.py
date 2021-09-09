from ..messages.handler import BaseHandler
from ...utils.snowflake import snowflake


class SnowFlakeRequestHandler(BaseHandler):

    async def do(self, *args, **kwargs):
        count = int(kwargs.get('count'))
        return {
            'data': [snowflake() for _ in range(count)]
        }
