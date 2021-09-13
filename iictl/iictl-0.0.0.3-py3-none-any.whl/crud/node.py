from kubernetes.client import CoreV1Api
from kubernetes.client import AppsV1Api

def list_node(**kwargs):
    api = CoreV1Api()

    pod_list = api.list_node(
        **kwargs,
    )
    
    return pod_list.to_dict()['items']