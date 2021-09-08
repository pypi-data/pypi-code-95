import json
import aiomysql
from datetime import datetime, date
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result

from tracardi.service.storage.helpers.source_reader import read_source
from tracardi_mysql_connector.model.configuration import Configuration
from tracardi_mysql_connector.model.connection import Connection


class MysqlConnectorAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'MysqlConnectorAction':

        configuration = Configuration(**kwargs)
        source = await read_source(configuration.source.id)
        connection = Connection(**source.config)

        plugin = MysqlConnectorAction(**kwargs)
        plugin.pool = await connection.connect()

        return plugin

    def __init__(self, **kwargs):
        self.pool = None
        if 'query' not in kwargs:
            raise ValueError("Please define query.")

        self.query = kwargs['query']
        self.timeout = kwargs['timeout'] if 'timeout' in kwargs else None

    async def run(self, payload):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(self.query)
                result = await cursor.fetchall()
                result = [self.to_dict(record) for record in result]
                return Result(port="result", value={"result": result})

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    @staticmethod
    def to_dict(record):

        def json_default(obj):
            """JSON serializer for objects not serializable by default json code"""

            if isinstance(obj, (datetime, date)):
                return obj.isoformat()

            return obj.decode('utf-8')

        j = json.dumps(dict(record), default=json_default)
        return json.loads(j)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi_mysql_connector.plugin',
            className='MysqlConnectorAction',
            inputs=["payload"],
            outputs=['result'],
            version='0.1.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "source": {
                    "id": None
                },
                "query": None
            }

        ),
        metadata=MetaData(
            name='Mysql connector',
            desc='Connects to mysql and reads data.',
            type='flowNode',
            width=200,
            height=100,
            icon='mysql',
            group=["Connectors"]
        )
    )
