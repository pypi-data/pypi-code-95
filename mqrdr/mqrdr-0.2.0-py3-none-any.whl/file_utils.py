''' MQRDR

Article file upload utils (modified from https://docs.figsh.com/#upload_files)

'''

import hashlib
import json
import os
# import config
import requests
from requests.exceptions import HTTPError
from mqrdr import settings, utils


BASE_URL = settings.BASE_URL
CHUNK_SIZE = 1048576


#
# Article file upload utils (modified from https://docs.figsh.com/#upload_files)
#

def raw_issue_request(token, method, url, data=None, binary=False):
    headers = utils.create_token_header(token)

    if data is not None and not binary:
        data = json.dumps(data)
    response = requests.request(method, url, headers=headers, data=data)
    try:
        response.raise_for_status()
        try:
            data = json.loads(response.content)
        except ValueError:
            data = response.content
    except HTTPError as error:
        raise

    return data


def issue_request(token, method, endpoint, *args, **kwargs):
    return raw_issue_request(token, method, f'{BASE_URL}/{endpoint}', *args, **kwargs)


def get_file_check_data(file_name):
    with open(file_name, 'rb') as fin:
        md5 = hashlib.md5()
        size = 0
        data = fin.read(CHUNK_SIZE)
        while data:
            size += len(data)
            md5.update(data)
            data = fin.read(CHUNK_SIZE)
        return md5.hexdigest(), size


def initiate_new_upload(token, article_id, file_name):
    endpoint = 'account/articles/{}/files'
    endpoint = endpoint.format(article_id)

    md5, size = get_file_check_data(file_name)

    data = {'name': os.path.basename(file_name),
            'md5': md5,
            'size': size}
    initial_result = issue_request(token, 'POST', endpoint, data=data)

    result = raw_issue_request(token, 'GET', initial_result['location'])

    return result


def complete_upload(token, article_id, file_id):
    return issue_request(token, 'POST', 'account/articles/{}/files/{}'.format(article_id, file_id))


def upload_parts(token, file_info, file_path):
    url = '{upload_url}'.format(**file_info)
    result = raw_issue_request(token, 'GET', url)
    with open(file_path, 'rb') as fin:
        for part in result['parts']:
            upload_part(token, file_info, fin, part)


def upload_part(token, file_info, stream, part):
    udata = file_info.copy()
    udata.update(part)
    url = '{upload_url}/{partNo}'.format(**udata)

    stream.seek(part['startOffset'])
    data = stream.read(part['endOffset'] - part['startOffset'] + 1)

    raw_issue_request(token, 'PUT', url, data=data, binary=True)

