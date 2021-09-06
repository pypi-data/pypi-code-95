from kubernetes.client import CoreV1Api
from kubernetes.client import AppsV1Api
from iictl.crud.tools import get_object_by_owner
from iictl.utils.exception import NotFoundError

def get_pod_name_by_ii_name(name, namespace):
    api = AppsV1Api()
    deployment_list = api.list_namespaced_deployment(namespace)
    deployment_name = get_object_by_owner(
        deployment_list,
        name,
    )
    
    replica_set_list = api.list_namespaced_replica_set(namespace)
    replica_set_name = get_object_by_owner(
        replica_set_list,
        deployment_name,
    )
    
    api = CoreV1Api()
    pod_list = api.list_namespaced_pod(namespace)
    pod_name = get_object_by_owner(
        pod_list,
        replica_set_name,
    )
    
    return pod_name

def get_pod_name_by_label_selector(namespace, label_selector):
    """
        If pod exist -> return first pod name
        else -> raise NotFoundError
    """
    api = CoreV1Api()

    pod_list = api.list_namespaced_pod(
        namespace='notebook',
        label_selector=label_selector,
    )
    
    if len(pod_list.items) == 0:
        raise NotFoundError
        
    pod_name = pod_list.items[0].metadata.name
    
    return pod_name

def get_pod_names_by_label_selector(namespace, label_selector):
    """
        If pod exist -> return pod list
        else -> return empty list
    """
    api = CoreV1Api()

    pod_list = api.list_namespaced_pod(
        namespace='notebook',
        label_selector=label_selector,
    )
    
    pod_names = [it.metadata.name for it in pod_list.items]
    
    return pod_names

def get_pod_log(name, namespace, follow=False, tail=None):
    api = CoreV1Api()

    return api.read_namespaced_pod_log(
        name=name,
        namespace=namespace,
        follow=follow,
        tail_lines=tail,
        _preload_content=False,
    ).stream()