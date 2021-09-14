import urllib.request
import requests
from bs4 import BeautifulSoup
from .util import checkDir

def pdfDownload(pmid, doi):
    url = 'https://sci-hub.se/{}'.format(doi)
    r = requests.get(url, allow_redirects=True)
    html = r.content
    soup = BeautifulSoup(html, 'html.parser')
    pdf_url = soup.embed['src']
    # print(pdf_url)
    response = urllib.request.urlopen(pdf_url)   
    save_path = checkDir('./pdf')
    with open('{}/{}.pdf'.format(save_path, pmid), 'wb') as f:
        f.write(response.read())
    print('{} Downloaded - {}'.format(pmid, doi))