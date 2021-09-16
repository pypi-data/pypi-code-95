from bs4 import BeautifulSoup, Comment
import tldextract
from urllib.parse import urlparse, urljoin

def tag_visible(element):
    """
    Take in element, see if it is visible on the page.
    :param element:
    :return:
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def pre_process_url(url):
    """
    Return a Standard, Lower URL without the HTML ids in link
    :param url:
    :return: processed url
    """

    url = url.split('#')[0]
    url = url.strip().lower()
    try:
        if url[-1] == '/':
            url = url[0:-1]
    except Exception as e:
        pass
    return url



def process_url(url):
    url = pre_process_url(url)

    url_object = {}
    url_object['url'] = url
    extraction = tldextract.extract(url)
    url_parse = urlparse(url)
    url_object['subdomain'] = extraction[0]
    url_object['domain'] = extraction[1]
    url_object['suffix'] = extraction[2]
    url_object['scheme'] = url_parse[0]
    url_object['netloc'] = url_parse[1]
    url_object['path'] = url_parse[2]
    url_object['params'] = url_parse[3]
    url_object['query'] = url_parse[4]
    url_object['fragment'] = url_parse[5]
    url_object['length'] = len(str(url))
    url_object['home_page'] = url_parse[0] + '://'+ url_parse[1]
    url_object['length'] = len(url)



    return url_object


def format_link(origin_url, destination_url):
    return urljoin(origin_url, destination_url)




