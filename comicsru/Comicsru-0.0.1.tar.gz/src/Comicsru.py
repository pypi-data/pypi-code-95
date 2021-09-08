import requests
from bs4 import BeautifulSoup
import os
import sys
from urllib.request import Request, urlopen
import shutil
from shutil import make_archive

base_url = 'https://readcomicsonline.ru/'

def get_summary(comic_name):
    try:
        url=f'{base_url}comic/{comic_name}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml') 
        summary = soup.find('p')
        print(summary.text)
    except:
        print('Error')
        sys.exit()    

def suggest_random():
    try:
        random_url = f'{base_url}random'
        response = requests.get(random_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        random_title = soup.title
        random_comic = random_title.text
        print(random_comic)
    except:
        print('Error')
        sys.exit()

def download_comic(get_url,format):
    try:
        html_text = requests.get(get_url).text
        soup = BeautifulSoup(html_text, 'lxml')
        divs = soup.find("div", id="all")
        img = divs.find_all('img')
        directory = get_url.replace('https://readcomicsonline.ru/comic/','').replace('/','-ch-')
    except:
        print('Error')  
        sys.exit()  
    try:
        os.mkdir(directory)
    except:
        pass    
    for l in img:
        link = l.get('data-src')
        filename = link[-7:]
        full_path = '{}/{}'.format(directory, filename)
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        web = urlopen(req)
        with open(full_path, 'wb') as f:
            f.write(web.read())
    if format == 'cbz':
        make_archive(directory, 'zip', root_dir=f'./{directory}')
        my_file = f'{directory}.zip'
        base = os.path.splitext(my_file)[0]
        os.rename(my_file, base + '.cbz')
        shutil.rmtree(directory)
        print('completed!')
    elif format == 'zip':
        make_archive(directory, 'zip', root_dir=f'./{directory}')
        shutil.rmtree(directory) 
        print('completed!')   
    elif format == 'jpg':
        exit    
    else:
        print(f'{format} format not allowed. Try jpg, zip or cbz')    