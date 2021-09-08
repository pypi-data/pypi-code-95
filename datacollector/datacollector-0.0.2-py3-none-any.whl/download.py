import urllib.request
import requests
from bs4 import BeautifulSoup

def pdfDownload(pmid, doi):
    url = 'https://sci-hub.se/{}'.format(doi)
    r = requests.get(url, allow_redirects=True)
    html = r.content
    soup = BeautifulSoup(html, 'html.parser')
    pdf_url = soup.embed['src']
    print(pdf_url)
    response = urllib.request.urlopen(pdf_url)    
    with open('./pdf/{}.pdf'.format(pmid), 'wb') as f:
        f.write(response.read())