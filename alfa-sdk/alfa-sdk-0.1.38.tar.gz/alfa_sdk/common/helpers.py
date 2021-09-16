import json
import pkg_resources
import semantic_version as semver
import zipfile
import yaml

from alfa_sdk.common.exceptions import (
    UnknownServiceError,
    ServiceEnvironmentError,
    SemanticVersionError,
    AlfaConfigError,
    ValidationError
)


class EndpointHelper:
    def __init__(self, *, alfa_env, alfa_id=None, region=None):
        resource_path = "/".join(("common", "data", "endpoints.json"))
        file = pkg_resources.resource_string("alfa_sdk", resource_path)

        alfa_id = alfa_id or "public"
        data = json.loads(file)[alfa_id]

        self.services = data["services"]
        self.hostname = data["hostname"]
        self.domain = data["domain"]
        self.alfa_env = alfa_env
        self.region = region or "eu-central-1"

    def resolve(self, service, path=""):
        if service not in self.services:
            known_services = ", ".join(sorted(self.services.keys()))
            raise UnknownServiceError(service_name=service, known_service_names=known_services)

        if self.alfa_env not in self.services[service]:
            raise ServiceEnvironmentError(service_name=service, environment=self.alfa_env)

        host = self.services[service][self.alfa_env]
        protocol = "https"
        if isinstance(host, list):
            protocol, host = host

        base_url = self.hostname.format(
            protocol=protocol, host=host, region=self.region, domain=self.domain[self.alfa_env]
        )
        return "{}{}".format(base_url, path)


class VersionHelper:
    @staticmethod
    def get(version):
        if type(version) is semver.Version:
            return version

        try:
            return semver.Version(version)
        except:
            raise SemanticVersionError(version=version)

    @staticmethod
    def increment(version):
        version = VersionHelper.get(version)
        version = version.next_patch()
        return str(version)

    @staticmethod
    def latest(versions):
        valid = [VersionHelper.get(x) for x in versions if semver.validate(x)]
        if not any(valid):
            return VersionHelper.get("0.0.0")

        version = max(valid)
        return version


class AlfaConfigHelper:
    @staticmethod
    def extract_from_package(file_path):
        message = "Failed to extract config in .zip package"
        try:
            with zipfile.ZipFile(file_path) as zip:
                if "alfa.yml" not in zip.namelist():
                    raise AlfaConfigError(message=message, error="alfa.yml not found in package")

                file = zip.read("alfa.yml")
                return file
        except Exception as err:
            raise AlfaConfigError(message=message, error=str(err))

    @staticmethod
    def load(file_path, is_package=False):
        file = None

        try:
            if is_package:
                file = AlfaConfigHelper.extract_from_package(file_path)
            else:
                file = open(file_path, "r").read()
        except AlfaConfigError:
            raise
        except Exception as err:
            raise AlfaConfigError(message="Failed to read file from path", error=str(err))

        try:
            conf = yaml.safe_load(file)
        except Exception as err:
            raise AlfaConfigError(message="Failed to parse alfa.yml", error=str(err))

        return conf
