import functools
import hashlib
import logging
import os
import os.path
import sys
from typing import Callable, List

# These are symbolic links used for locks in standard users directories
__standard_exceptions__ = {
    'lock',  # firefox lock, $HOME/.mozilla/firefox/[XXX].default/lock
    'SingletonCookie',  # chrome lock, /home/mark/.config/google-chrome/SingletonCookie
    'SingletonLock',  # chrome lock, /home/mark/.config/google-chrome/SingletonLock
    'SingletonSocket',  # chrome lock, /home/mark/.config/google-chrome/SingletonSocket
}

import requests
from bs4 import BeautifulSoup


def yield_bad_symlinks(
    folder: str = ".",
    use_standard_exceptions: bool = True,
    onerror: Callable = None,
):
    """
    remove bad symbolic links from a folder.

    Control this functions verbosity using the python logging framework
    :param folder:
    :param use_standard_exceptions:
    :param onerror: passed to os.walk
    :return:
    """
    logger = logging.getLogger(__name__)
    for root, _dirs, files in os.walk(folder, onerror=onerror):
        for file in files:
            if use_standard_exceptions and file in __standard_exceptions__:
                continue
            full = os.path.join(root, file)
            if os.path.islink(full):
                dereference_name = os.readlink(full)
                if not os.path.isabs(dereference_name):
                    dereference_name = os.path.join(root, dereference_name)
                if not os.path.exists(dereference_name):
                    logger.debug("found bad symlink [%s]...", full)
                    yield full


def diamond_lines(filenames: List[str]):
    if not filenames:
        for line in sys.stdin.readlines():
            yield line
    else:
        for filename in filenames:
            with open(filename, 'rt') as file_handle:
                for line in file_handle:
                    yield line


def checksum(file_name: str = None, algorithm: str = None) -> str:
    """
    calculate a checksum of a file. You dictate which algorithm.
    If you want to see all algorithms try:
    hashlib.algorithms_available
    :param file_name:
    :param algorithm:
    :return:
    """
    block_size = 65536
    with open(file_name, mode='rb') as f:
        hash_object = hashlib.new(algorithm)
        for buf in iter(functools.partial(f.read, block_size), b''):
            hash_object.update(buf)
    return hash_object.hexdigest()


def remove_bad_symlinks(folder: str, use_standard_exceptions: bool) -> None:
    """
    remove bad symbolic links from a folder
    """
    for full in yield_bad_symlinks(
            folder=folder,
            use_standard_exceptions=use_standard_exceptions,
            onerror=error,
    ):
        print(f"removing [{full}]")
        os.unlink(full)


def download_file_from_google_drive(file_id: str, destination: str):
    url = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(url, params={'id': file_id}, stream=True)
    assert response.status_code == 200, "bad request"
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(url, params=params, stream=True)

    save_response_content(response, destination)


def gdrive_download_link(url: str):
    """
    Here is a sample google drive shared url:
    https://drive.google.com/file/d/1EbAbRUKowIi7ZL8fcktsEqj-gvcyq0a6/view?usp=sharing
    This function will:
    - download the link
    - extract the name of the file from the link
    - extract the id of the file from the link
    - use the method above to download the file
    :param url: the share link you got from google
    :return:
    """
    session = requests.Session()

    response = session.get(url=url, stream=True)
    assert response.status_code == 200, response.status_code
    bad_document = response.content.decode()
    # document, _errors = tidy_document(bad_document, options={
    #    'doctype': 'omit',
    # })
    s = BeautifulSoup(bad_document)
    print(s)
    # dom = xml.dom.minidom.parseString(document)
    # print(dom)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None


def save_response_content(response, destination):
    chunk_size = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def error(args):
    raise args
