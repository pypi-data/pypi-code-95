from typing import List, Tuple, Dict, Optional
from kubernetes.client.api_client import ApiClient
from kubernetes.client import CoreV1Api
from iictl.format.persistent_volume_claim import get_persistent_volume_claim_format
from kubernetes.client.exceptions import ApiException
from iictl.utils.exception import AlreadyExistError, NotFoundError

def create_persistent_volume_claim(
    name: str,
    namespace: str,
    size: str,
):  
    pvc_spec = get_persistent_volume_claim_format(
        name=name,
        namespace=namespace,
        size=size,
    )
    
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        try:
            return api.create_namespaced_persistent_volume_claim(
                namespace=namespace,
                body=pvc_spec
            )
        except ApiException as e:
            if e.status == 409:
                raise AlreadyExistError
            
            raise e

def list_persistent_volume_claim(
    namespace: str,
):      
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        return api.list_namespaced_persistent_volume_claim(
            namespace=namespace,
        )

def patch_persistent_volume_claim(
    name: str,
    namespace: str,
    body: dict,
):  
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        try:
            return api.patch_namespaced_persistent_volume_claim(
                name=name,
                namespace=namespace,
                body=body
            )
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError
            
            raise e

def read_persistent_volume_claim(
    name: str,
    namespace: str,
):  
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        try:
            return api.read_namespaced_persistent_volume_claim(
                name=name,
                namespace=namespace,
            )
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError
            
            raise e


def delete_persistent_volume_claim(
    name: str,
    namespace: str,
):  
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        try:
            return api.delete_namespaced_persistent_volume_claim(
                name=name,
                namespace=namespace,
            )
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError
            
            raise e
