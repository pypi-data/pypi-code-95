from typing import List

from openapi_client.models import OrmKernelImage, ResponseKernelImage
from savvihub import vessl_api
from savvihub.organization import _get_organization_name


def read_kernel_image(image_id: int) -> ResponseKernelImage:
    return vessl_api.kernel_image_read_api(image_id=image_id)


def list_kernel_images(**kwargs) -> List[OrmKernelImage]:
    """List kernel images

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.kernel_image_list_api(
        organization_name=_get_organization_name(**kwargs),
    ).results
