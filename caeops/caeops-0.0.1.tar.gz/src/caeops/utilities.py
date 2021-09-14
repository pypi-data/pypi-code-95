import argparse
import json
from typing import List
import yaml

from colorama import Fore

from caeops.configurations import read
from caeops.global_settings import PROJECT_ROOT

configfile = open(PROJECT_ROOT + "/caeops/config.json", "r")
data = json.load(configfile)
configfile.close()
TenantRegistrationUrl = data.get("TenantRegistrationUrl", "")
CentralizedMetricsUrl = data.get("CentralizedMetricsUrl", "")
KubernetesProvisioningUrl = data.get("KubernetesProvisioningUrl", "")


def to_camel_case(input_str, separator="_"):
    components = input_str.split(separator)
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def json_keys_to_camel_case(json):
    new_json = {}
    for key in json:
        camel_key = to_camel_case(key)
        new_json[camel_key] = json[key]
    return new_json


def validate_mandatory_fields(payload: dict, mandatory_fields: List[str]) -> object:
    """
    Validates the payload for any missing mandatory fields
    :param payload: Payload to validate
    :param mandatory_fields: Fields that are mandatory
    :return: object => Exit in case of missing fields else return none
    """
    # Extract the payload keys
    payload_keys = list(payload.keys())
    # Find the missing mandatory fields
    missing_args = list(
        filter(
            lambda f: to_camel_case(f, separator="-") not in payload_keys
            or not payload[to_camel_case(f, separator="-")],
            mandatory_fields,
        )
    )
    # If there is at least one missing field => throw error
    if missing_args:
        msg = "Missing required arguments : "
        msg += ", ".join(list(map(lambda f: f"'--{f}'", missing_args)))
        msg += "\nSee --help for more information"
        print(msg)
        exit(1)
    return


def generate_auth_headers(token):
    return {"Authorization": "Bearer " + read(token)}


def color_print_command(cmd):
    print(Fore.CYAN, cmd)


def success(payload):
    print(Fore.GREEN, payload)


def failure(payload):
    return Fore.RED + "Unsuccessful", payload


class LoadFromFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        with values as f:
            # print(f.read().split())
            # parse arguments in the file and store them in the target namespace
            parser.parse_args(f.read().split(), namespace)


def restructure_with_sub_object(actual_object: dict, sub_object_key: str) -> dict:
    """
    Adjusts the payload based on the resource type selected.
    Eg:{
      "name": "someone",
      "age": 30,
      "employeeId": "1234",
      "employeeManagerId": "5678"
    }
    will be converted to
    {
      "name": "someone",
      "age": 30,
      "employee": {
        "id": "1234",
        "managerId": "5678"
      }
    }
    :param actual_object: The actual object that needs to be modified
    :param sub_object_key: The key of the sub object to extract
    :return: Modified object
    """
    sub_object = {}
    # Extract the keys
    keys = list(actual_object.keys())
    # For each key
    for k in keys:
        # Filter the keys that start with the given resource => Eg: { "kubernetesClusterName": "sample" }
        if k.startswith(sub_object_key):
            # Remove the resource prefix => { "ClusterName": "sample" }
            new_key = k.replace(sub_object_key, "")
            # Make the first character lower case => { "clusterName": "sample" }
            new_key = new_key[0].lower() + new_key[1:]
            # Add the new key as sub object => { "kubernetes" : { "clusterName": "sample" } }
            sub_object[new_key] = actual_object[k]
            del actual_object[k]
    actual_object[sub_object_key] = sub_object
    return actual_object


def read_yaml(yaml_file_path) -> str:
    """
    Read the contents of the given yaml file as YAML
    :param yaml_file_path: Path to the YAML file
    :return: String in YAML format
    """
    with open(yaml_file_path) as f:
        yaml_data = yaml.safe_dump(yaml.safe_load(f))
        f.close()
    return yaml_data


def read_yaml_as_json(yaml_file_path):
    """
    Read the contents of the given yaml file as json
    :param yaml_file_path: Path to the YAML file
    :return: String in YAML format
    """
    with open(yaml_file_path) as f:
        json_data = json.dumps(yaml.safe_load(f), indent=2)
        f.close()
    return json_data


def read_json(json_file_path):
    """
    Read the contents of the given json file as json
    :param json_file_path: Path to the json file
    :return: String in YAML format
    """
    with open(json_file_path) as f:
        json_data = json.loads(f.read())
    return json.dumps(json_data, indent=2)


def read_json_as_yaml(json_file_path):
    """
    Read the contents of the given json file as YAML
    :param json_file_path: Path to the json file
    :return: String in YAML format
    """
    with open(json_file_path) as f:
        yaml_data = json.loads(f.read())
    return yaml.safe_dump(yaml.safe_load(json.dumps(yaml_data)), sort_keys=False)


def convert_dict_to_yaml(input_dict: dict):
    """
    Read the contents of the given json file as YAML
    :param input_dict: input dict
    :return: String in YAML format
    """
    return yaml.safe_dump(yaml.safe_load(json.dumps(input_dict)), sort_keys=False)
