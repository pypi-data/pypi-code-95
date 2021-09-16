import sys
import traceback
import aiopg
from aiopg import sa
from django.conf import settings


class PostgresClient:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = getattr(self, 'loop')
        self.log = getattr(self, 'log')
        self.app_name = getattr(self, 'app_name')

        try:
            self.PG_CONN = settings.DATABASES.get('default')
            self.PG_NAME = self.PG_CONN['NAME']
            self.PG_USER = self.PG_CONN['USER']
            self.PG_PASSWORD = self.PG_CONN['PASSWORD']
            self.PG_HOST = self.PG_CONN['HOST']
            self.PG_PORT = self.PG_CONN['PORT']
            self.PG_DSN = f"dbname={self.PG_NAME} user={self.PG_USER} password={self.PG_PASSWORD} host={self.PG_HOST} port={self.PG_PORT}"
            self.loop.run_until_complete(self._postgres())
            self.log.info(f"open: {self.PG_NAME}@{self.PG_HOST}:{self.PG_PORT}", name='postgres')
        except Exception as e:
            self.log.critical(f"connection error: {e.__repr__()}, dsn: {self.PG_DSN}", tb=traceback.format_exc(), name='postgres')
            sys.exit()

    async def _postgres(self):
        self.postgres = await aiopg.sa.create_engine(self.PG_DSN, loop=self.loop, maxsize=500)

    def close(self):
        self.postgres.close()
        self.loop.run_until_complete(self.postgres.wait_closed())
        self.log.info(f"close: {self.PG_NAME}@{self.PG_HOST}", name='postgres')

