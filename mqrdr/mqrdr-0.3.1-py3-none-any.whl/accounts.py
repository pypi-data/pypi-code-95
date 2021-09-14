# ----------------------------------------------------------------------------------------------------------------------
# Accounts
# ----------------------------------------------------------------------------------------------------------------------


import requests
from mqrdr import utils


def list_accounts(base_url, token, page=1, page_size=10, impersonated_id=None):
    ''' List accounts
    Returns the accounts for which the account has administrative privileges (assigned and inherited).

    token: Repository authorization token (string)
    page: Page number. Used for pagination with page_size
    page_size: The number of results included on a page. Used for pagination with page
    impersonated_id: Account ID of user being impersonated (optional, integer)
    '''

    headers = utils.create_token_header(token)

    if impersonated_id:
        request_url = f"{BASE_URL}/account/institution/accounts?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{BASE_URL}/account/institution/accounts?page={page}&page_size={page_size}"
    
    response = requests.get(request_url, headers=headers)

    return response.json()


def search_accounts(base_url, token, data, page=1, page_size=10, impersonated_id=None):
    ''' Search accounts

    token: Repository authorization token (string)
    data: Dictionary object containing project filters
    page: Page number. Used for pagination with page_size
    page_size: The number of results included on a page. Used for pagination with page
    impersonated_id: Account ID of user being impersonated (optional, integer)
    '''

    headers = utils.create_token_header(token)

    if impersonated_id:
        request_url = f"{BASE_URL}/account/institution/accounts/search?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{BASE_URL}/account/institution/accounts/search?page={page}&page_size={page_size}"
    
    response = requests.post(request_url, json=data, headers=headers)

    return response.json()


def view_account_details(base_url, token, account_id):
    ''' View account details

    token: Repository authorization token (string)
    author_id: ID of the account (integer)
    '''

    headers = utils.create_token_header(token)
    
    request_url = f"{BASE_URL}/account/institution/users/{account_id}"

    response = requests.get(request_url, headers=headers)

    return response.json()