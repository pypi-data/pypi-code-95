import os
from parser_libraries import functions as f
from bs4 import BeautifulSoup
import logging
import logging.handlers
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

URL = 'http://audit.gov.ru/structure/'
HOST = 'http://audit.gov.ru'


def get_person(link):
    try:
        html = f.get_html(link['link'])
        soup = BeautifulSoup(html.text, 'html.parser')
        image_link = soup.find('div', class_='photo').find('img').get('src')
        cont = soup.find('div', class_='info').get_text().split(maxsplit=3)
        name = []
        for i in range(0, 3):
            name.append(cont[i].lower())
        bday = soup.find('div', class_='expand-field').get_text().lower()
        ind = bday.find('родил')
        bday = f.get_dig_date(bday[ind:bday.find('год')].split(maxsplit=1)[1])
        return {'position_id': link['work'], 'first_name': name[1], 'middle_name': name[2], 'last_name': name[0],
                'bday': bday['day'], 'bmonth': bday['month'], 'byear': bday['year'], 'image_link': image_link, 'link': link['link']}
    except:
        return 1

def parser():
    log.debug(f"The script {__name__} starts working")
    links = []
    people = []
    html = f.get_html(URL)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('div', class_='structure-row flex')
        items.append(soup.find('div', class_='structure-row flex structure-row--apparat-first'))
        for item in items:
            arr = item.find_all('a')
            for ar in arr:
                work = ar.get_text()
                work = work.split(maxsplit=3)
                work = f.get_work(work[-1].lower(), 34)
                if work != -1:
                    links.append({'link': HOST + ar.get('href'), 'work': work})
        for link in links:
            box = get_person(link)
            if box == 1:
                return [{'code': 1, 'script': os.path.basename(__file__)}]
            people.append(box)
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]

if __name__ == '__main__':
    print(parser())