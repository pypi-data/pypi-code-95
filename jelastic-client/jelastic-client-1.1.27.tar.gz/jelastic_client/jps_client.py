import json

from .core import ApiClient, BaseClient, who_am_i


class JpsClient(BaseClient):
    jelastic_group = "marketplace"

    jelastic_class = "jps"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    def install_from_file(self, filename: str, env_name: str = None, settings: dict = None) -> str:
        with open(filename) as file:
            manifest_content = file.read()
            return self.install(manifest_content, env_name, settings)

    def install(self, manifest_content: str, env_name: str = None, settings: dict = None) -> str:
        response = self._execute(
            who_am_i(),
            jps=manifest_content,
            envName=env_name,
            skipNodeEmails=True,
            settings=json.dumps(settings)
        )

        return response["successText"]

    def get_engine_version(self) -> str:
        response = self._execute(
            who_am_i()
        )

        return response["version"]
