from typing import List

from openapi_client.models.orm_kernel_resource_spec import OrmKernelResourceSpec
from savvihub import vessl_api
from savvihub.organization import _get_organization_name
from savvihub.util.exception import InvalidKernelResourceSpecError


def read_kernel_resource_spec(
    kernel_resource_spec_name: str, **kwargs
) -> OrmKernelResourceSpec:
    """Read kernel resource spec

    Keyword args:
        organization_name (str): override default organization
    """
    kernel_resource_specs = list_kernel_resource_specs(**kwargs)
    kernel_resource_specs = {x.name: x for x in kernel_resource_specs}

    if kernel_resource_spec_name not in kernel_resource_specs:
        raise InvalidKernelResourceSpecError(
            f"Kernel resource spec not found: {kernel_resource_spec_name}"
        )
    return kernel_resource_specs[kernel_resource_spec_name]


def list_kernel_resource_specs(**kwargs) -> List[OrmKernelResourceSpec]:
    """List kernel resource specs

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.kernel_resource_spec_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results


def _configure_custom_kernel_resource_spec(
    processor_type: str = None,
    cpu_limit: float = None,
    memory_limit: float = None,
    gpu_type: str = None,
    gpu_limit: int = None,
) -> OrmKernelResourceSpec:
    return OrmKernelResourceSpec(
        processor_type=processor_type,
        cpu_type="Any",
        cpu_limit=cpu_limit,
        memory_limit=f"{memory_limit}Gi",
        gpu_type=gpu_type,
        gpu_limit=gpu_limit,
    )
