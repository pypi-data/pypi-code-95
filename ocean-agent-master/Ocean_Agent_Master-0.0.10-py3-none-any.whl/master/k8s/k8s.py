from kubernetes import client, config, utils
import yaml


def get_api_client():
    config.load_kube_config()
    return client.ApiClient()


def create_resources_from_yaml(manifest):
    yml_document_all = yaml.safe_load_all(manifest)
    for yml_document in yml_document_all:
        if yml_document: # Calico YAML에서 비어있는 YAML 항목이 None으로 들어오고 있으므로 주의
            utils.create_from_dict(get_api_client(), yml_document)
