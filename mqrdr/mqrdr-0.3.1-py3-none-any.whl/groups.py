# ----------------------------------------------------------------------------------------------------------------------
# Groups
# ----------------------------------------------------------------------------------------------------------------------

from mqrdr import utils


def list_groups(base_url, token, page=1, page_size=10, impersonated_id=None):
    ''' List all groups

    token: Repository authorization token (string, required)
    page: Page number. Used for pagination with page_size (integer, optional, default = 1)
    page_size: The number of results included on a page. Used for pagination with page (integer, optional, default = 10)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/institution/groups?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/institution/groups?page={page}&page_size={page_size}"

    return utils.endpoint_get(token, request_url)
