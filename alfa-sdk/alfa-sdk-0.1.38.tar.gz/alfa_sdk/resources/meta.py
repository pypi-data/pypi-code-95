import os
import requests

from alfa_sdk.common.base import BaseResource
from alfa_sdk.common.exceptions import ResourceNotFoundError, AlfaError
from alfa_sdk import resources


class MetaUnit(BaseResource):
    def __init__(self, environment_id, tag, **kwargs):
        self.environment_id = environment_id
        self.tag = tag
        super().__init__(**kwargs)

    def _fetch_data(self):
        self.local = self.session.context.get("__RUN_LOCAL__", False)
        try:
            body = {"algorithmEnvironmentId": self.environment_id, "tag": self.tag}
            return self.session.request(
                "get", "meta", "/api/Units/getUnitForAlgorithmEnvironment", json=body
            )
        except AlfaError as err:
            if self.local:
                return {
                    "id": None,
                    "description": "",
                    "buildConfigurations": [],
                    "watchConfigurations": [],
                }
            raise err

    def _fill_data(self):
        data = self.get_data()
        self.id = data.get("id")
        self.description = data.get("description")
        self.build_configurations = data.get("buildConfigurations")
        self.watch_configurations = data.get("watchConfigurations")

    #

    def get_environment(self):
        return resources.AlgorithmEnvironment(self.environment_id, session=self.session)

    def get_active_instance(self):
        if self.local:
            instances = self.list_instances()
            if instances:
                active_instance = max(instances, key=lambda x: x["id"])
                return LocalMetaInstance(active_instance["path"])

        body = {"algorithmEnvironmentId": self.environment_id, "tag": self.tag}
        data = self.session.request("get", "meta", "/api/Units/getActiveInstance", json=body)
        return MetaInstance(data["id"], data=data, session=self.session)

    def list_instances(self):
        if self.local:
            instances_dir = os.path.join(
                ".", "build", ".instances", *self.environment_id.split(":"), self.tag
            )
            if not os.path.isdir(instances_dir):
                instances_dir = os.path.join(
                    ".", "build", ".instances", self.environment_id, self.tag
                )
                if not os.path.isdir(instances_dir):
                    return []

            return sorted(
                [
                    {
                        "id": os.path.splitext(f)[0],
                        "path": os.path.join(instances_dir, f),
                    }
                    for f in os.listdir(instances_dir)
                    if os.path.isfile(os.path.join(instances_dir, f))
                ],
                key=lambda x: x["id"],
            )

        params = {"algorithmEnvironmentId": self.environment_id, "tag": self.tag}
        return self.session.request(
            "get", "meta", "/api/Units/getAlgorithmInstances", params=params
        )

    def store_activate_instance(self, file_path):
        params = {"algorithmEnvironmentId": self.environment_id, "tag": self.tag}
        files = {"file": open(file_path, "rb")}
        return self.session.request(
            "post",
            "meta",
            "/api/Units/storeActivateInstance",
            params=params,
            files=files,
        )

    def store_instance(self, file):
        params = {"algorithmEnvironmentId": self.environment_id, "tag": self.tag}
        if isinstance(file, bytes):
            files = {"file": file}
        else:
            files = {"file": open(file, "rb")}

        return self.session.request(
            "post", "meta", "/api/Units/storeInstance", params=params, files=files
        )


class MetaInstance(BaseResource):
    def __init__(self, instance_id, **kwargs):
        self.id = instance_id
        super().__init__(**kwargs)

    def _fetch_data(self):
        return self.session.request("get", "meta", "/api/AlgorithmInstances/{}".format(self.id))

    def _fill_data(self):
        data = self.get_data()
        self.active = data.get("active")
        self.environment_id = data.get("algorithmEnvironmentId")
        self.unit_id = data.get("unitId")

    #

    def get_unit(self):
        data = self.session.request("get", "meta", "/api/Units/{}".format(self.unit_id))
        return MetaUnit(self.environment_id, data["tag"], session=self.session)

    def fetch_file(self):
        url = self.session.request(
            "get", "meta", "/api/AlgorithmInstances/downloadInstance/{}".format(self.id)
        )

        res = requests.get(url, allow_redirects=True)
        return res.content


class LocalMetaInstance(BaseResource):
    def __init__(self, path, **kwargs):
        self.path = path
        self._data = kwargs.get("data", {})

    def _fetch_data(self):
        pass

    def _fill_data(self):
        pass

    def fetch_file(self):
        with open(self.path, "rb") as instance_file:
            return instance_file.read()
