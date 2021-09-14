# ----------------------------------------------------------------------------------------------------------------------
# Articles
#
# Note: All functions relate to artciles belonging to the current (or impersonated user). For public articles use the public API calls
# 
# ----------------------------------------------------------------------------------------------------------------------

import requests
from mqrdr import utils, file_utils


def list_articles(base_url, token, page=1, page_size=10, impersonated_id=None):
    ''' List articles belonging to the current user

    token: Repository authorization token (string, required)
    page: Page number. Used for pagination with page_size (integer, optional, default = 1)
    page_size: The number of results included on a page. Used for pagination with page (integer, optional, default = 10)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/articles?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/articles?page={page}&page_size={page_size}"

    return utils.endpoint_get(token, request_url)


def search_articles(base_url, token, data):
    ''' Search articles belonging to the current user

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    data: Dictionary object containing article filters
    '''

    request_url = f"{base_url}/account/articles/search"

    return utils.endpoint_post(token, request_url, data)


def view_article(base_url, token, article_id, impersonated_id=None):
    ''' View an article belonging to the current user

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string, required)
    article_id: ID of the article (integer, required)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/articles/{article_id}?impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/articles/{article_id}"
    
    return utils.endpoint_get(token, request_url)


def create_article(base_url, token, data):
    ''' Create a new article

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    data: Dictionary object containing new project article attributes
    '''

    request_url = f"{base_url}/account/articles"
    
    return utils.endpoint_post(token, request_url, data)


def update_article(base_url, token, article_id, data):
    ''' Update an article belonging to the current user

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    data: Dictionary object containing updated article attributes
    '''

    request_url = f"{base_url}/account/articles/{article_id}"

    return utils.endpoint_put(token, request_url, data)


def delete_article(base_url, token, article_id):
    ''' Delete an article belonging to the current user

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    request_url = f"{base_url}/account/articles/{article_id}"

    return utils.endpoint_delete(token, request_url)


def list_article_files(base_url, token, article_id, page=1, page_size=10, impersonated_id=None):
    ''' List an article's files

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    page: Page number. Used for pagination with page_size (integer, optional, default = 1)
    page_size: The number of results included on a page. Used for pagination with page (integer, optional, default = 10)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/articles/{article_id}/files?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/articles/{article_id}/files?page={page}&page_size={page_size}"

    return utils.endpoint_get(token, request_url)


def view_article_file(base_url, token, article_id, file_id, impersonated_id=None):
    ''' View details of a file belonging to an article

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/articles/{article_id}/files/{file_id}?impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/articles/{article_id}/files/{file_id}"

    return utils.endpoint_get(token, request_url)


def download_article_file(base_url,token, article_id, file_id):
    ''' Download an article file

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    '''

    request_url = f"{base_url}/articles/{article_id}/files/{file_id}"
    response = utils.endpoint_get(token, request_url)

    filename = response.json()['name']
    download_url = response.json()['download_url']

    r = requests.get(download_url, allow_redirects=True)
    open(filename, 'wb').write(r.content)
    return r
    

def upload_article_file(token, article_id, file_path):
    ''' Upload a file to an article

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the existing article to upload file to (integer)
    file_path: Full path to the file to upload
    '''

    file_info = file_utils.initiate_new_upload(token, article_id, file_path)
    print(file_info)
    file_utils.upload_parts(token, file_info, file_path)
    file_utils.complete_upload(token, article_id, file_info['id'])


def delete_article_file(base_url, token, article_id, file_id):
    ''' Delete an article file

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    '''

    request_url = f"{base_url}/account/articles/{article_id}/files/{file_id}"

    return utils.endpoint_delete(token, request_url)


def publish_article(base_url, token, article_id):
    ''' Publish an article

    base_url: Base URL of the figshare repository being used (e.g. https://api.figsh.com/v2)
    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    request_url = f"{base_url}/account/articles/{article_id}/publish"
    
    return utils.endpoint_post(token, request_url, data=None)