from typing import List, Tuple, Dict, Optional
from kubernetes.client.models import V1PersistentVolumeClaim, V1ObjectMeta, V1PersistentVolumeClaimSpec, V1ResourceRequirements

def get_persistent_volume_claim_format(
    name: str,
    namespace: str,
    size: str,
) -> V1PersistentVolumeClaim:
    return V1PersistentVolumeClaim(
        metadata=V1ObjectMeta(
            name=name,
            namespace=namespace,
        ),
        spec=V1PersistentVolumeClaimSpec(
            access_modes=['ReadWriteMany'],
            resources=V1ResourceRequirements(
                requests={
                    'storage': size,
                }
            ),            
        ),
    )
