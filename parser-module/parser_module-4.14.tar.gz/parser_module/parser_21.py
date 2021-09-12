from parser_libraries import functions as f
from bs4 import BeautifulSoup
import time
import os
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL_JUDGE = 'http://www.ksrf.ru/ru/Info/Judges/Pages/default.aspx'
HOST = 'http://www.ksrf.ru/ru/Info/Judges/Pages/'


def get_people(html):
    people = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('ul', class_='dfwp-column dfwp-list')
    for item in items:
        item = item.find('ul', class_='dfwp-list')
        cases = item.find_all('li', class_='dfwp-item')
        for case in cases:
            case = case.find('a')
            if case.get('title') != '':
                case = case.get('href').replace('\t', '')
                case = get_link(case)
            else:
                case = ''
            if case != '':
                box = get_person(HOST+case)
                if box == 1:
                    return 1
                people.append(box)
    return people


def get_person(link):
    try:
        if link != '':
            html = f.get_html(link)
            soup = BeautifulSoup(html.text, 'html.parser')
            item = soup.find('table', class_='s4-wpTopTable')
            image_link = item.find('img').get('src')
            item = item.find('tr').find('table').find_all('tr')
            name = item[0].get_text().lower().strip(' ')
            name = f.get_name(name)
            work = item[1].get_text().lower()
            text = item[2].get_text()
            ind = text.find(' ')+1
            ind_2 = text.find('года')-1
            ind_3 = text.find('г.')-1
            if ind_2 == -2:
                ind_2 = ind_3
            text = text[ind:ind_2]
            text = f.get_dig_date(text)
            person = {
                'position_id': f.get_work(work, 21),
                'first_name': name[1],
                'middle_name': name[2],
                'last_name': name[0],
                'bday': text['day'],
                'bmonth': text['month'],
                'byear': text['year'],
                'image_link': image_link,
                'link': link,
            }
        return person
    except:
        return 1

def get_link(str):
    ind = str.find('j')
    str = str[ind:]
    return str


def parser():
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(URL_JUDGE)
    if html.status_code == 200:
        people = get_people(html.text)
        if people == 1:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
        time.sleep(5)
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]