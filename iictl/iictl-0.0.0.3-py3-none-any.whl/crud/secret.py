from typing import List, Tuple, Dict, Optional
from kubernetes.client import CoreV1Api
from kubernetes.client.api_client import ApiClient
from kubernetes.client.exceptions import ApiException
from iictl.utils.exception import AlreadyExistError, NotFoundError
from kubernetes.client.models import V1Secret

def create_secret(
    name: str,
    namespace: str,
    secret: V1Secret,
):  
    
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        try:
            return api.create_namespaced_secret(
                namespace=namespace,
                body=secret,
            )
        except ApiException as e:
            if e.status == 409:
                raise AlreadyExistError
            
            raise e

def list_secret(
    namespace: str,
):      
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        return api.list_namespaced_secret(
            namespace=namespace,
        ).to_dict()['items']

def read_secret(
    name: str,
    namespace: str,
):  
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        try:
            return api.read_namespaced_secret(
                name=name,
                namespace=namespace,
            )
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError
            
            raise e


def delete_secret(
    name: str,
    namespace: str,
):  
    with ApiClient() as api_client:
        api = CoreV1Api(api_client)
        
        try:
            return api.delete_namespaced_secret(
                name=name,
                namespace=namespace,
            )
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError
            
            raise e
