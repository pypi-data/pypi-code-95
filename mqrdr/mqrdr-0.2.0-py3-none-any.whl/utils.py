''' MQRDR UTILITY FUNCTIONS

Utility functions for Macquarie University Research Data Repository library

'''

# from mqrdr import settings
import requests


# BASE_URL = settings.BASE_URL


def create_token_header(token):
    ''' Create a http header object with token embedded
    
    '''

    header =  {'Authorization': 'token ' + token}

    return header


def endpoint_get(token, request_url):
    ''' Make a GET call

    '''

    headers = create_token_header(token)
    response = requests.get(request_url, headers=headers)
    
    return response


def endpoint_post(token, request_url, data):
    ''' Make a POST call

    '''

    headers = create_token_header(token)
    response = requests.post(request_url, headers=headers, json=data)

    return response


def endpoint_put(token, request_url, data):
    ''' Make a PUT call

    '''

    headers = create_token_header(token)
    response = requests.put(request_url, headers=headers, json=data)
    print(response)

    return response


def endpoint_delete(token, request_url):
    ''' Make a DELETE call

    '''

    headers = create_token_header(token)
    response = requests.delete(request_url, headers=headers)

    return response
