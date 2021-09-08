from typing import Optional
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result

from tracardi_mongodb_connector.model.client import MongoClient
from tracardi_mongodb_connector.model.configuration import PluginConfiguration, MongoConfiguration

from tracardi.service.storage.helpers.source_reader import read_source


class MongoConnectorAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'MongoConnectorAction':
        plugin = MongoConnectorAction(**kwargs)
        source = await read_source(plugin.config.source.id)
        mongo_config = MongoConfiguration(
            **source.config
        )

        plugin.client = MongoClient(mongo_config)

        return plugin

    def __init__(self, **kwargs):
        self.config = PluginConfiguration(**kwargs)
        self.client = None  # type: Optional[MongoClient]

    async def run(self, payload):
        result = await self.client.find(self.config.mongo.database, self.config.mongo.collection, self.config.query)
        return Result(port="payload", value={"result": result})

    # async def close(self):
    #     self.client.close()


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi_mongodb_connector.plugin',
            className='MongoConnectorAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.1.7',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "source": {
                    "id": None,
                },
                "mongo": {
                    "database": None,
                    "collection": None
                },
                "query": {}
            }

        ),
        metadata=MetaData(
            name='Mongo connector',
            desc='Connects to mongodb and reads data.',
            type='flowNode',
            width=200,
            height=100,
            icon='mongo',
            group=["Connectors"]
        )
    )
