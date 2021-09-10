from typing import List

from openapi_client.models import (
    CustomClusterUpdateAPIPayload,
    ResponseKernelClusterInfo,
    ResponseKernelClusterNodeInfo,
)
from savvihub import vessl_api
from savvihub.organization import _get_organization_name


def read_cluster(cluster_name: str, **kwargs) -> ResponseKernelClusterInfo:
    """Read cluster

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.cluster_read_api(
        cluster_name=cluster_name,
        organization_name=_get_organization_name(**kwargs),
    )


def list_clusters(**kwargs) -> List[ResponseKernelClusterInfo]:
    """List clusters

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.all_cluster_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).clusters


def delete_cluster(cluster_name: str, **kwargs) -> object:
    """Delete custom cluster

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.custom_cluster_delete_api(
        cluster_name=cluster_name,
        organization_name=_get_organization_name(**kwargs),
    )


def rename_cluster(
    cluster_name: str, new_cluster_name: str, **kwargs
) -> ResponseKernelClusterInfo:
    """Rename custom cluster

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.custom_cluster_update_api(
        cluster_name=cluster_name,
        organization_name=_get_organization_name(**kwargs),
        custom_cluster_update_api_payload=CustomClusterUpdateAPIPayload(
            name=new_cluster_name,
        ),
    )


def list_cluster_nodes(
    cluster_name: str, **kwargs
) -> List[ResponseKernelClusterNodeInfo]:
    """List custom cluster nodes

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.custom_cluster_node_list_api(
        cluster_name=cluster_name,
        organization_name=_get_organization_name(**kwargs),
    ).nodes
