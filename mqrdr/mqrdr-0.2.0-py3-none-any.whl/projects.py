# ----------------------------------------------------------------------------------------------------------------------
# Projects
# ----------------------------------------------------------------------------------------------------------------------

import requests
from mqrdr import utils, file_utils


def list_projects(base_url, token, page=1, page_size=10, impersonated_id=None):
    ''' List projects belonging to the current user

    token: Repository authorization token (string, required)
    page: Page number. Used for pagination with page_size (integer, optional, default = 1)
    page_size: The number of results included on a page. Used for pagination with page (integer, optional, default = 10)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/projects?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/projects?page={page}&page_size={page_size}"

    return utils.endpoint_get(token, request_url)


def search_projects(base_url, token, data):
    ''' Search projects belonging to the current user

    token: Repository authorization token (string)
    data: Dictionary object containing project filters
    '''

    request_url = f"{base_url}/account/projects/search"

    return utils.endpoint_post(token, request_url, data)


def view_project(base_url, token, project_id, impersonated_id=None):
    ''' View a project belonging to the current user

    token: Repository authorization token (string, required)
    project_id: ID of the project (integer, required)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/projects/{project_id}?impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/projects/{project_id}"
    
    return utils.endpoint_get(token, request_url)


def create_project(base_url, token, data):
    ''' Create a private project belonging to the current user

    token: Repository authorization token (string)
    data: Dictionary object containing project parameters
    '''

    request_url = f"{base_url}/account/projects"

    return utils.endpoint_post(token, request_url, data)


def update_project(base_url, token, project_id, data):
    ''' Update a project belonging to the current user

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    data: Dictionary object containing updated project attributes
    '''

    request_url = f"{base_url}/account/projects/{project_id}"

    return utils.endpoint_put(token, request_url, data)


def delete_project(base_url, token, project_id):
    ''' Delete a project belonging to the current user

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    '''

    request_url = f"{base_url}/account/projects/{project_id}"

    return utils.endpoint_delete(token, request_url)


def list_project_articles(base_url, token, project_id, page=1, page_size=10, impersonated_id=None):
    ''' List a project's articles

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    page: Page number. Used for pagination with page_size (integer, optional, default = 1)
    page_size: The number of results included on a page. Used for pagination with page (integer, optional, default = 10)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/projects/{project_id}/articles?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/projects/{project_id}/articles?page={page}&page_size={page_size}"
    
    return utils.endpoint_get(token, request_url)


def view_project_article(base_url, token, project_id, article_id, impersonated_id=None):
    ''' View an article belonging to a project

    token: Repository authorization token (string, required)
    project_id: ID of the project (integer, required)
    article_id: ID of the article (integer, required)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/projects/{project_id}/articles/{article_id}?impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/projects/{project_id}/articles/{article_id}"
    
    return utils.endpoint_get(token, request_url)


def create_project_article(base_url, token, project_id, data):
    ''' Create a new project article

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    data: Dictionary object containing new project article attributes
    '''

    request_url = f"{base_url}/account/projects/{project_id}/articles"
    
    return utils.endpoint_post(token, request_url, data)


def update_project_article(base_url, token, article_id, data):
    ''' Update a project article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    data: Dictionary object containing updated article attributes
    '''

    request_url = f"{base_url}/account/articles/{article_id}"

    return utils.endpoint_put(token, request_url, data)


def delete_project_article(base_url, token, project_id, article_id):
    ''' Delete a project article

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    article_id: ID of the article (integer)
    '''

    request_url = f"{base_url}/account/projects/{project_id}/articles/{article_id}"

    return utils.endpoint_delete(token, request_url)
    

def list_project_article_files(base_url, token, project_id, article_id, page=1, page_size=10, impersonated_id=None):
    ''' List a project article's files

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    article_id: ID of the article (integer)
    page: Page number. Used for pagination with page_size (integer, optional, default = 1)
    page_size: The number of results included on a page. Used for pagination with page (integer, optional, default = 10)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/projects/{project_id}/articles/{article_id}/files?page={page}&page_size={page_size}&impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/projects/{project_id}/articles/{article_id}/files?page={page}&page_size={page_size}"

    return utils.endpoint_get(token, request_url)
    

def view_project_article_file(base_url, token, project_id, article_id, file_id, impersonated_id=None):
    ''' List a project article's files

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by RDR admin accounts)
    '''

    if impersonated_id:
        request_url = f"{base_url}/account/projects/{project_id}/articles/{article_id}/files/{file_id}?impersonate={impersonated_id}"
    else:
        request_url = f"{base_url}/account/projects/{project_id}/articles/{article_id}/files/{file_id}"

    return utils.endpoint_get(token, request_url)


def download_project_article_file(base_url,token, article_id, file_id):
    ''' Download a project article file

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


def upload_project_article_file(base_url,token, article_id, file_path):
    ''' Upload a file to a project article

    token: Repository authorization token (string)
    article_id: ID of the existing article to upload file to (integer)
    file_path: Full path to the file to upload
    '''

    file_info = file_utils.initiate_new_upload(token, article_id, file_path)
    file_utils.upload_parts(token, file_info, file_path)
    return file_utils.complete_upload(token, article_id, file_info['id'])


def delete_project_article_file(base_url, token, article_id, file_id):
    ''' Delete a project article file

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    '''

    request_url = f"{base_url}/account/articles/{article_id}/files/{file_id}"

    return utils.endpoint_delete(token, request_url)


def publish_project_article(base_url, token, article_id):
    ''' Publish a project article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    request_url = f"{base_url}/account/articles/{article_id}/publish"
    
    return utils.endpoint_post(token, request_url, data=None)


# ---------------------------------------------------------
# ---------------------------------------------------------


def invite_private_project_collaborator(base_url, token, project_id, data, impersonated_id=None):
    ''' Create a new private project article

    token: Repository authorization token (string)
    project_id: ID of the project (integer)
    data: Dictionary object containing project collaborator attributes
    impersonated_id: Account ID of user being impersonated (optional, integer)
    '''

    headers = utils.create_token_header(token)

    if impersonated_id:
        data["impersonate"] = impersonated_id

    request_url = f"{base_url}/account/projects/{project_id}/collaborators"

    response = requests.post(request_url, json=data, headers=headers)

    return response.json()
