from salesdredge.crawler.helpers import tag_visible, format_link, process_url
from salesdredge.helpers import hash_for_id

from bs4 import BeautifulSoup, Comment
import requests
import re


default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
# Scraped = True/False
# Error = True/False

def prepare_link(tag_type, tag_text, tag_link, doc):
    link_url_data = process_url(tag_link)
    link_id = link_url_data['url'].replace(link_url_data['scheme'], "")
    cross_domain = link_url_data['domain'] != doc['url']['domain']
    link = {
        "id": hash_for_id(link_id),
        "tag": tag_type,
        "text": tag_text,
        "url": link_url_data,
        'cross_domain': cross_domain
    }
    return link



def scrape(url, timeout=30, headers=None):
    if headers is None:
        headers = default_headers
    scraped = True
    error = False
    try:
        res = requests.get(url, timeout=timeout, headers=headers)
        html = res._content.decode('utf-8').replace('\n', ' ')
    except Exception as e:
        html = e
        error = True
        scraped = False

    return {"scraped": scraped, "error": error, "html": html, "url": url}


def process_page(page, custom_func=None):
    doc = {
        'error': page['error'],
        'scraped': page['scraped'],
        'url': process_url(page['url'])
    }
    doc['id'] = hash_for_id(doc['url']['url'].replace(doc['url']['scheme'], ""))

    if page['error'] == False and page['scraped'] == True:
        soup = BeautifulSoup(page['html'], 'html.parser')


        # Get Title
        try:
            doc['title'] = soup.title.text
        except:
            doc['title'] = ""

        # Get Description
        try:
            desc = soup.findAll(attrs={"name": re.compile(r"description", re.I)})
            doc['description'] = desc[0]['content']

        except:
            doc['description'] = ""

        # Get Visible Text
        visible_text_elements = [word.strip() for word in filter(tag_visible, soup.findAll(text=True))]
        visible_text_elements = [x for x in filter(lambda x: len(x) > 0, visible_text_elements)]
        text = ' '.join(visible_text_elements)
        doc['visible_text_elements'] = visible_text_elements
        doc['text'] = text

        # Get Links
        links = []
        hrefs = soup.findAll(attrs={"href": True})
        for href in hrefs:
            tag_type = href.name
            tag_text = href.text.strip()
            tag_link = format_link(page['url'], href['href'])
            links.append(prepare_link(tag_type, tag_text, tag_link, doc))
        srcs = soup.findAll(attrs={"src": True})
        for src in srcs:
            links.append(prepare_link(src.name, src.text, format_link(page['url'], src['src']), doc))
        doc['links'] = links

        # Get Header Text
        headers = soup.find_all(
            re.compile('^h[1-6]$'),
            text=True)
        headers = [{"tag": x.name, "text": x.text } for x in filter(tag_visible, headers)]
        doc['header_text'] = headers

        if custom_func:
            custom_func(soup, doc)
    return doc


# p = scrape('https://www.omnifund.com')
# process_page(p)

