from typing import List, Tuple, Dict, Optional
from kubernetes.client.api_client import ApiClient
from kubernetes.client import CustomObjectsApi
from kubernetes.client.exceptions import ApiException
from iictl.utils.exception import AlreadyExistError, NotFoundError

def create_integrated_instance(
    namespace: str,
    integrated_instance: dict,
):  
    with ApiClient() as api_client:
        custom_object = CustomObjectsApi(api_client)
        
        try:
            return custom_object.create_namespaced_custom_object(
                group='deep.est.ai',
                version='v1alpha',
                namespace=namespace,
                plural='integratedinstances',
                body=integrated_instance,
            )
        except ApiException as e:
            if e.status == 409:
                raise AlreadyExistError
            
            raise e

def list_integrated_instance(
    namespace: str,
):  
    with ApiClient() as api_client:
        custom_object = CustomObjectsApi(api_client)
        return custom_object.list_namespaced_custom_object(
            group='deep.est.ai',
            version='v1alpha',
            namespace=namespace,
            plural='integratedinstances',
        )

def delete_integrated_instance(
    namespace: str,
    name: str,
):  
    with ApiClient() as api_client:
        custom_object = CustomObjectsApi(api_client)
        
        try:
            return custom_object.delete_namespaced_custom_object(
                group='deep.est.ai',
                version='v1alpha',
                plural='integratedinstances',
                namespace=namespace,
                name=name,
            )
        except ApiException as e:
            if e.status == 404:
                raise NotFoundError
            
            raise e
