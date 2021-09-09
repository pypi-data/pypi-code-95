from tracardi_plugin_sdk.service.plugin_runner import run_plugin

from tracardi_mysql_connector.plugin import MysqlConnectorAction

init = dict(
    source= {
        "id": "x"
    },
    query="SELECT * from user;"
)
payload = {}


result = run_plugin(MysqlConnectorAction, init, payload)
print(result)
