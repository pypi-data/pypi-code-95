# ----------------------------------------------------------------------------------------------------------------------
# Articles
# ----------------------------------------------------------------------------------------------------------------------


import requests
from mqrdr import settings, utils, file_utils


BASE_URL = settings.BASE_URL


# Public Articles

def list_public_articles(token, page=1, page_size=10):
    ''' List all public articles

    token: Repository authorization token (string)
    page: Page number. Used for pagination with page_size
    page_size: The number of results included on a page. Used for pagination with page
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/articles?page={page}&page_size={page_size}"
    response = requests.get(request_url, headers=headers)

    return response.json()



def search_public_articles(token, data):
    ''' Search public articles

    token: Repository authorization token (string)
    data: Dictionary object containing search attributes
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/articles/search"
    response = requests.post(request_url, json=data, headers=headers)

    return response.json()


def view_public_article(token, article_id):
    ''' View a public article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/articles/{article_id}"
    response = requests.get(request_url, headers=headers)

    return response.json()


def list_public_article_files(token, article_id):
    ''' List a public article's files

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/articles/{article_id}/files"
    response = requests.get(request_url, headers=headers)

    return response.json()


def view_public_article_file(token, article_id, file_id):
    ''' View a public article file

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/articles/{article_id}/files/{file_id}"
    response = requests.get(request_url, headers=headers)

    return response.json()


def download_public_article_file(token, article_id, file_id):
    ''' Download a public article file

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/articles/{article_id}/files/{file_id}"
    response = requests.get(request_url, headers=headers)

    filename = response.json()['name']
    download_url = response.json()['download_url']

    r = requests.get(download_url, allow_redirects=True)
    open(filename, 'wb').write(r.content)


# Private Articles

def list_private_articles(token, page=1, page_size=10, impersonated_id=None):
    ''' List private articles

    token: Repository authorization token (string, required)
    page: Page number. Used for pagination with page_size (integer, optional, default = 1)
    page_size: The number of results included on a page. Used for pagination with page (integer, optional, default = 10)
    impersonated_id: Account ID of user being impersonated (integer, optional, only usable by admin accounts)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles?page={page}&page_size={page_size}"
    response = requests.get(request_url, headers=headers)

    return response.json()


def create_private_article(token, data):
    ''' Create a private article

    token: Repository authorization token (string)
    data: Dictionary object containing new article attributes
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles"
    response = requests.post(request_url, json=data, headers=headers)

    return response.json()


def create_private_article_file(token, article_id, file_path):
    ''' Upload a file to an existing private article

    token: Repository authorization token (string)
    article_id: ID of the existing article to upload file to (integer)
    file_path: Full path to the file to upload
    '''

    file_info = file_utils.initiate_new_upload(token, article_id, file_path)
    file_utils.upload_parts(token, file_info, file_path)
    file_utils.complete_upload(token, article_id, file_info['id'])


def search_private_articles(token, data):
    ''' Search private articles

    token: Repository authorization token (string)
    data: Dictionary object containing search attributes
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/search"
    response = requests.post(request_url, json=data, headers=headers)

    return response.json()


def view_private_article(token, article_id):
    ''' View a private article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}"
    response = requests.get(request_url, headers=headers)

    return response.json()


def list_private_article_authors(token, article_id):
    ''' List a private article's authors

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}/authors"
    response = requests.get(request_url, headers=headers)

    return response.json()


def list_private_article_files(token, article_id):
    ''' List a private article's files

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}/files"
    response = requests.get(request_url, headers=headers)

    return response.json()


def view_private_article_file(token, article_id, file_id):
    ''' View a private article file

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}/files/{file_id}"
    response = requests.get(request_url, headers=headers)

    return response.json()


def download_private_article_file(token, article_id, file_id):
    ''' Download a private article file

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    file_id: ID of the file (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}/files/{file_id}"
    response = requests.get(request_url, headers=headers)

    filename = response.json()['name']
    download_url = response.json()['download_url']

    r = requests.get(download_url, headers=headers, allow_redirects=True)
    open(filename, 'wb').write(r.content)


def update_private_article(token, article_id, data):
    ''' Update a private article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    data: Dictionary object containing article updates
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}"
    response = requests.put(request_url, json=data, headers=headers)

    return response


def delete_private_article(token, article_id):
    ''' Delete a private article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}"
    response = requests.delete(request_url, headers=headers)

    return response


def embargo_private_article(token, article_id, data):
    ''' Embargo a private article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    data: Dictionary object containing embargo details
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}/embargo"
    response = requests.put(request_url, json=data, headers=headers)

    # return response.json()
    return response


def publish_private_article(token, article_id):
    ''' Publish a private article

    token: Repository authorization token (string)
    article_id: ID of the article (integer)
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/articles/{article_id}/publish"
    response = requests.post(request_url, headers=headers)

    return response.json()
