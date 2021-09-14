# ----------------------------------------------------------------------------------------------------------------------
# Authors
# ----------------------------------------------------------------------------------------------------------------------


import requests
from mqrdr import settings, utils


BASE_URL = settings.BASE_URL


def search_authors(token, data):
    ''' Search authors

    token: Repository authorization token (string)
    data: Dictionary object containing author search filters
    '''

    headers = utils.create_token_header(token)

    request_url = f"{BASE_URL}/account/authors/search"
    
    response = requests.post(request_url, json=data, headers=headers)

    return response.json()


def view_author_details(token, author_id):
    ''' View author details

    token: Repository authorization token (string)
    author_id: ID of the author (integer)
    '''

    headers = utils.create_token_header(token)
    
    request_url = f"{BASE_URL}/account/authors/{author_id}"

    response = requests.get(request_url, headers=headers)

    return response.json()