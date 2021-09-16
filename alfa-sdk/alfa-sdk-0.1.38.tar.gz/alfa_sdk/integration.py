from alfa_sdk.common.base import BaseClient
from alfa_sdk.resources import (
    Integration,
    IntegrationEnvironment,
    Release,
)


class IntegrationClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    #

    def get_integration(self, integration_id):
        return Integration(integration_id, session=self.session)

    def get_environment(self, environment_id):
        return IntegrationEnvironment(environment_id, session=self.session)

    def get_release(self, release_id):
        return Release(release_id, session=self.session)

    #

    def get_context(self):
        return self.session.context

    def get_integration_from_context(self):
        environment = self.get_environment_from_context()
        if environment is None:
            return None
        return environment.get_integration()

    def get_environment_from_context(self):
        if not self.session.context or (
            "environmentId" not in self.session.context
            and "algorithmEnvironmentId" not in self.session.context
        ):
            return None

        environment_id = self.session.context.get(
            "environmentId", self.session.context.get("algorithmEnvironmentId")
        )
        return self.get_environment(environment_id)

    #

    def list_integrations(self):
        params = {"teamId": self.user["teamId"]}
        return self.session.request("get", "ais", "/api/Integrations", params=params)

    def list_environments(self, integration_id):
        integration = self.get_integration(integration_id)
        return integration.list_environments()

    def list_releases(self, environment_id):
        environment = self.get_environment(environment_id)
        return environment.list_releases()

    #

    def invoke(self, integration_id, environment, function, problem, **kwargs):
        return self.session.invoke(
            integration_id,
            environment,
            problem,
            function_name=function,
            function_type="integration",
            **kwargs,
        )

    def deploy(self, integration_id, environment, version, file_path, **kwargs):
        integration = self.get_integration(integration_id)
        environment = integration.get_environment(environment)
        return environment.deploy(version, file_path, **kwargs)
