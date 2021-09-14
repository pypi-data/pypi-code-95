from typing import List, Tuple, Dict, Optional

def get_integrated_instance_format(
    name: str,
    image: str,
    command: Optional[List[str]] = None,
    lb: Optional[List[Tuple[str, int]]] = None,
    envs: Optional[List[Tuple[str, str]]] = None,
    volume_mounts: Optional[List[Tuple[str, str, bool]]] = None,
    working_dir: Optional[str] = None,
    gpus: Optional[int] = None,
    cpus: Optional[str] = None,
    node_selector: Optional[Dict[str, str]] = None,
    image_pull_secret: Optional[str] = None,
):
    lb = [
        {
            'domain': domain,
            'port': port,
        } for port, domain in lb
    ]
    
    envs = [
        {
            'name': name,
            'value': value,
        } for name, value in envs
    ]
    
    volume_mounts = [
        {
            'pvcName': name,
            'mountPath': path,
            'readOnly': ro,
        } for name, path, ro in volume_mounts
    ]
    
    resources = {
        'requests': {
            'cpu': '0',
        },
        'limits': {
            'nvidia.com/gpu': gpus,
            'cpu': cpus,
        },
    }
    
    
    return {
        'apiVersion': 'deep.est.ai/v1alpha',
        'kind': 'IntegratedInstance',
        'metadata': {
            'name': name,
        },
        'spec': {
            'image': image,
            'command': command,
            'lb': lb,
            'envs': envs,
            'volumeMounts': volume_mounts,
            'workingDir': working_dir,
            'resources': resources,
            'nodeSelector': node_selector,
            'imagePullSecret': image_pull_secret,
        }
    }