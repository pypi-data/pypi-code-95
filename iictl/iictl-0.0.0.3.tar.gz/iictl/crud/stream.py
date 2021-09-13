from kubernetes.client import CoreV1Api
from kubernetes.client import AppsV1Api
from kubernetes.stream import stream

from iictl.crud.tools import get_object_by_owner

def get_exec_stream_pod(name, namespace, command, stdin=False, tty=False):
    api = CoreV1Api()
    
    return stream(
        api.connect_post_namespaced_pod_exec,
        name=name,
        namespace=namespace,
        command=list(command),
        stdout=True,
        stderr=True,
        stdin=stdin,
        tty=tty,
        _preload_content=False,
    )
    
def get_attach_stream_pod(name, namespace, stdin=False, tty=False):
    api = CoreV1Api()
    
    return stream(
        api.connect_post_namespaced_pod_attach,
        name=name,
        namespace=namespace,
        stdout=True,
        stderr=True,
        stdin=stdin,
        tty=tty,
        _preload_content=False,
    )
    
def get_attach_stream_pod(name, namespace, stdin=False, tty=False):
    api = CoreV1Api()
    
    return stream(
        api.connect_post_namespaced_pod_attach,
        name=name,
        namespace=namespace,
        stdout=True,
        stderr=True,
        stdin=stdin,
        tty=tty,
        _preload_content=False,
    )