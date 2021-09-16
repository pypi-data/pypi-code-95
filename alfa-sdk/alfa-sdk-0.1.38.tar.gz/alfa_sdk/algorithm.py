from alfa_sdk.common.base import BaseClient
from alfa_sdk.common.exceptions import ValidationError
from alfa_sdk.secrets import SecretsClient
from alfa_sdk.resources import (
    Algorithm,
    AlgorithmEnvironment,
    Release,
    MetaUnit,
)


class AlgorithmClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secrets = SecretsClient(session=self.session)

    #

    def get_algorithm(self, algorithm_id, *, team_id=None):
        return Algorithm(algorithm_id, session=self.session, team_id=team_id)

    def get_environment(self, environment_id):
        return AlgorithmEnvironment(environment_id, session=self.session)

    def get_release(self, release_id):
        return Release(release_id, session=self.session)

    def get_mass_customization_unit(self, environment_id, tag):
        return MetaUnit(environment_id, tag, session=self.session)

    #

    def get_context(self):
        return self.session.context

    def get_algorithm_from_context(self):
        environment = self.get_environment_from_context()
        if environment is None:
            return None
        return environment.get_algorithm()

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

    def get_active_instance_from_context(self, unit_tag):
        context = self.session.context
        if not context or (
            "environmentId" not in context and "algorithmEnvironmentId" not in context
        ):
            raise ValidationError(error="No environment defined.")
        environment_id = context.get("environmentId", context.get("algorithmEnvironmentId"))

        meta_unit = self.get_mass_customization_unit(environment_id, unit_tag)
        active_instance = meta_unit.get_active_instance()
        return active_instance.fetch_file()

    #

    def list_algorithms(self):
        params = {"teamId": self.user["teamId"]}
        return self.session.request("get", "baas", "/api/Algorithms/getList", params=params)

    def list_environments(self, algorithm_id):
        algorithm = self.get_algorithm(algorithm_id)
        return algorithm.list_environments()

    def list_releases(self, environment_id):
        environment = self.get_environment(environment_id)
        return environment.list_releases()

    def list_mass_customization_units(self, environment_id):
        environment = self.get_environment(environment_id)
        return environment.list_mass_customization_units()

    #

    def invoke(self, algorithm_id, environment, problem, **kwargs):
        return self.session.invoke(algorithm_id, environment, problem, **kwargs)

    def deploy(self, algorithm_id, environment, version, file_path, **kwargs):
        algorithm = self.get_algorithm(algorithm_id)
        environment = algorithm.get_environment(environment)
        return environment.deploy(version, file_path, **kwargs)

    #

    def store_kpi(self, kpis, entity=None, time=None):
        run_id = self.session.context.get("algorithmRunId")
        environment = self.get_environment_from_context()
        if environment is None:
            raise ValidationError(error="EnvironmentId is not defined.")
        return environment.store_kpi(kpis, entity, run_id, time)
