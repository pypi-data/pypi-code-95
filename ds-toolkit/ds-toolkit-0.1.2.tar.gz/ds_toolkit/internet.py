from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import requests

from ds_toolkit.logger import get_logger


log = get_logger()


def get_links_from_webpage(url, extension_filters=None, base_url=''):
    """

    Args:
        url (string):
        extension_filters (list):
        base_url  (str): Prepend this url to each link
    Returns:
        list:
    """
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f'Bad response: \n{resp.text}')

    soup = BeautifulSoup(resp.content, 'html.parser')
    elements = soup.find_all('a')

    if base_url.endswith('/'):
        base_url = base_url[:-1]

    if extension_filters is None:
        extension_filters = []

    links = []
    for element in elements:
        link = element.get('href')

        if link:
            if extension_filters:
                for extension in extension_filters:
                    if link.lower().endswith(extension.lower()):
                        if base_url:
                            links.append(f'{base_url}{link}')
                        else:
                            links.append(link)
                        break

            else:
                links.append(link)
    return links


def download_file(url, folder_path='', file_name='', file_path=''):
    """
    Downloads a file from the web.

    Args:
        url (str): Url to download file
        folder_path (str): Destination folder
        file_name (str): Save file name as
        file_path (str): Full file path
    """

    if not file_path:
        if not folder_path:
            raise Exception("Missings args - file_path or folder_path & file_name")
        if not file_name:
            file_name = url.split('/')[-1]
            log.debug(f'No file_name passed, using file_name from url path: {file_name}')
        file_path = folder_path + file_name

    log.debug(f'Downloading file | URL: {url} | File path: {file_path}')
    urlretrieve(url, file_path)
    return file_path
