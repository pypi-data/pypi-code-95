from datetime import datetime
from alfa_sdk.common.base import BaseResource
from alfa_sdk.common.exceptions import ResourceDeletionError, ValidationError
from alfa_sdk.common.helpers import VersionHelper
from alfa_sdk import resources

FUNCTION_TYPE = "algorithm"


class Algorithm(BaseResource):
    def __init__(self, algorithm_id, **kwargs):
        self.id = algorithm_id
        super().__init__(**kwargs)

    def _fetch_data(self):
        params = {"environments": True}
        return self.session.request(
            "get", "baas", "/api/Algorithms/getInfo/{}".format(self.id), params=params
        )

    def _fill_data(self):
        data = self.get_data()
        self.name = data.get("name")
        self.description = data.get("description")
        self.type = data.get("type")

    #

    def invoke(self, environment, problem, **kwargs):
        return self.session.invoke(self.id, environment, problem, **kwargs)

    def list_environments(self):
        return self._data.get("environments")

    def get_environment(self, name):
        team_id = self.team_id if self.team_id else self.user["teamId"]
        environment_id = "{}:{}:{}".format(team_id, self.id, name)
        return AlgorithmEnvironment(environment_id, session=self.session)

    def create_environment(self, name, *, invoke_function=None):
        return AlgorithmEnvironment.create(
            self.session, self.id, name, invoke_function=invoke_function
        )


class AlgorithmEnvironment(BaseResource):
    def __init__(self, environment_id, **kwargs):
        self.id = environment_id
        super().__init__(**kwargs)

    def _fetch_data(self):
        return self.session.request(
            "get", "baas", "/api/AlgorithmEnvironments/getInfo/{}".format(self.id)
        )

    def _fill_data(self):
        data = self.get_data()
        self.name = data.get("name")
        self.algorithm_id = data.get("algorithmId")

    #

    def invoke(self, problem, **kwargs):
        return self.session.invoke(self.algorithm_id, self.name, problem, **kwargs)

    def get_algorithm(self):
        return Algorithm(self.algorithm_id, session=self.session)

    def list_registrations(self):
        data = self.get_data()
        return {
            "invoke": data.get("invokeFunction"),
            "pre-process": data.get("preProcessFunction"),
            "post-process": data.get("postProcessFunction"),
            "build": data.get("buildFunction"),
            "score": data.get("scoreFunction"),
        }

    #

    @staticmethod
    def create(session, algorithm_id, name, *, invoke_function=None):
        body = {"algorithmId": algorithm_id, "name": name}
        if invoke_function is not None:
            body["invokeFunction"] = invoke_function

        data = session.request(
            "post", "baas", "/api/AlgorithmEnvironments/addEnvironment", json=body
        )
        return AlgorithmEnvironment(environment_id=data["id"], session=session, data=data)

    def delete(self, force=False):
        releases = self.list_releases()
        active = [x["active"] for x in releases]
        if any(active) and not force:
            raise ResourceDeletionError(
                resource=type(self),
                error="Cannot delete an environment with an active release.",
            )

        body = {"algorithmEnvironmentId": self.id}
        return self.session.request(
            "post", "baas", "/api/AlgorithmEnvironments/deleteEnvironment", json=body
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

    #

    def get_mass_customization_unit(self, tag):
        return resources.MetaUnit(self.id, tag, session=self.session)

    def list_mass_customization_units(self):
        params = {"algorithmEnvironmentId": self.id}
        return self.session.request(
            "get", "meta", "/api/Units/getUnitsForAlgorithmEnvironment", params=params
        )

    #

    def store_kpi(self, kpis, entity=None, run_id=None, time=None):
        if run_id is None:
            raise ValidationError(error="AlgorithmRunId is not defined.")

        if time is None:
            time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        if not isinstance(kpis, list):
            kpis = [kpis]

        for kpi in kpis:
            if not "time" in kpi:
                kpi["time"] = time
            if not "entity" in kpi:
                kpi["entity"] = entity
            if not "name" in kpi:
                raise ValidationError(error="No name for KPI defined.")
            if not "value" in kpi:
                raise ValidationError(error="No value for KPI defined.")

        body = {
            "algorithmEnvironmentId": self.id,
            "algorithmRunId": run_id,
            "data": kpis,
        }

        return self.session.request("POST", "watch", "/api/kpis/add", json=body)
