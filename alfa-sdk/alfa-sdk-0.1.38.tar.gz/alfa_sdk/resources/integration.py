from datetime import datetime
from alfa_sdk.common.base import BaseResource
from alfa_sdk.common.exceptions import ResourceDeletionError, ValidationError
from alfa_sdk.common.helpers import VersionHelper
from alfa_sdk import resources

FUNCTION_TYPE = "integration"


class Integration(BaseResource):
    def __init__(self, integration_id, **kwargs):
        self.id = integration_id
        super().__init__(**kwargs)

    def _fetch_data(self):
        return self.session.request("get", "ais", "/api/Integrations/{}".format(self.id))

    def _fill_data(self):
        data = self.get_data()
        self.name = data.get("name")
        self.description = data.get("description")

    #

    def invoke(self, environment, function_name, problem):
        return self.session.invoke(
            self.id, environment, problem, function_name=function_name, function_type=FUNCTION_TYPE
        )

    def list_environments(self):
        return self._data.get("environments")

    def get_environment(self, name):
        environment_id = "{}:{}".format(self.id, name)
        return IntegrationEnvironment(environment_id, session=self.session)

    def create_environment(self, name):
        return IntegrationEnvironment.create(self.session, self.id, name)


class IntegrationEnvironment(BaseResource):
    def __init__(self, environment_id, **kwargs):
        team_id, integration, environment = environment_id.split(":")
        self.environment = environment
        self.integration_id = "{}:{}".format(team_id, integration)
        self.id = environment_id
        super().__init__(**kwargs)

    def _fetch_data(self):
        return self.session.request(
            "get",
            "ais",
            "/api/Integrations/{}/environments/{}".format(self.integration_id, self.environment),
        )

    def _fill_data(self):
        data = self.get_data()
        self.name = data.get("name")

    #

    def invoke(self, function_name, problem):
        return self.session.invoke(
            self.integration_id,
            self.environment,
            problem,
            function_name=function_name,
            function_type=FUNCTION_TYPE,
        )

    def get_integration(self):
        return Integration(self.integration_id, session=self.session)

    def list_registrations(self):
        data = self.get_data()
        return {"functions": data.get("functions")}

    #

    @staticmethod
    def create(session, integration_id, name):
        body = {"name": name}
        data = session.request(
            "post", "ais", "/api/Integrations/{}/environments".format(integration_id), json=body
        )
        return IntegrationEnvironment(environment_id=data["id"], session=session, data=data)

    def delete(self, force=False):
        releases = self.list_releases()
        active = [x["active"] for x in releases]
        if any(active) and not force:
            raise ResourceDeletionError(
                resource=type(self),
                error="Cannot delete an environment with an active release.",
            )

        return self.session.request(
            "delete",
            "ais",
            "/api/Integrations/{}/environments/{}".format(self.integration_id, self.environment),
        )

    #

    def deploy(self, version, file_path, **kwargs):
        description = kwargs.get("description", None)
        release_notes = kwargs.get("release_notes", None)
        increment = kwargs.get("increment", False)

        if increment is True:
            releases = self.list_releases()
            new = VersionHelper.get(version)
            latest = VersionHelper.latest([x["version"] for x in releases])

            if new <= latest:
                new = VersionHelper.increment(latest)
                version = str(new)

        params = {
            "environmentId": self.id,
            "type": FUNCTION_TYPE,
            "version": version,
            "description": description,
            "releaseNotes": release_notes,
        }
        files = {"file": open(file_path, "rb")}
        data = self.session.request(
            "post", "release", "/api/Releases/upload", files=files, params=params
        )
        return resources.Release(data["id"], session=self.session, data=data)

    def get_active_release(self):
        releases = self.list_releases()
        active = [x for x in releases if x["active"] is True]
        if not any(active):
            return None

        data = active[0]
        return resources.Release(data["id"], session=self.session, data=data)

    def list_releases(self):
        params = {"environmentId": self.id, "type": FUNCTION_TYPE}
        return self.session.request("get", "release", "/api/Releases/getList", params=params)
