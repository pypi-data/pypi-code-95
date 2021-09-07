from typing import List

from openapi_client.models import (
    OrganizationCreateAPIPayload,
    ResponseOrganization,
    ResponseOrganizationInfo,
)
from savvihub import vessl_api
from savvihub.util.exception import InvalidOrganizationError


def read_organization(organization_name: str) -> ResponseOrganizationInfo:
    return vessl_api.organization_read_api(organization_name=organization_name)


def list_organizations() -> List[ResponseOrganization]:
    return vessl_api.organization_list_api().organizations


def create_organization(
    organization_name: str, region: str
) -> ResponseOrganizationInfo:
    return vessl_api.organization_create_api(
        organization_create_api_payload=OrganizationCreateAPIPayload(
            name=organization_name, region=region
        )
    )


def _get_organization_name(**kwargs) -> str:
    organization_name = kwargs.get("organization_name")
    if organization_name is not None:
        return organization_name
    if vessl_api.organization is not None:
        return vessl_api.organization.name
    raise InvalidOrganizationError("No organization selected.")
