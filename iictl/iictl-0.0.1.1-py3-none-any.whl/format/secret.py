from typing import List, Tuple, Dict, Optional
from kubernetes.client.models import V1Secret, V1ObjectMeta

def get_secret_format(
    name: str,
    data: str,
    type_: str,
) -> V1Secret:
    return V1Secret(
        metadata=dict(name=name),
        data=data,
        type=type_,
    )
