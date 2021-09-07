from typing import List

from openapi_client.models import (
    ModelCreateAPIPayload,
    ModelUpdateAPIPayload,
    ResponseModelDetail,
)
from savvihub import vessl_api
from savvihub.organization import _get_organization_name
from savvihub.project import _get_project_name


def read_model(version: int, **kwargs) -> ResponseModelDetail:
    """Read model

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    return vessl_api.model_read_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        version=version,
    )


def list_models(**kwargs) -> List[ResponseModelDetail]:
    """List models

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    return vessl_api.model_list_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
    ).results


def create_model(
    experiment_id: int, description: str = None, tags: List[str] = None, **kwargs
) -> ResponseModelDetail:
    """Create model

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    return vessl_api.model_create_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        model_create_api_payload=ModelCreateAPIPayload(
            workload_id=experiment_id,
            description=description,
            tag_names=tags,
        ),
    )


def update_model(version: int, description: str, **kwargs) -> ResponseModelDetail:
    """Update model

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    return vessl_api.model_update_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        version=version,
        model_update_api_payload=ModelUpdateAPIPayload(description=description),
    )


def delete_model(version: int, **kwargs) -> object:
    """Delete model

    Keyword args:
        organization_name (str): override default organization
        project_name (str): override default project
    """
    return vessl_api.model_delete_api(
        organization_name=_get_organization_name(**kwargs),
        project_name=_get_project_name(**kwargs),
        version=version,
    )
