from tracardi_mongodb_connector.plugin import MongoConnectorAction
from tracardi_plugin_sdk.service.plugin_runner import run_plugin


init = {
        "source": {
            "id": "x"
        },
        "mongo": {
            "database": "local",
            "collection": "startup_log"
        }
    }

payload = {}

result = run_plugin(MongoConnectorAction, init, payload)
print(result)

