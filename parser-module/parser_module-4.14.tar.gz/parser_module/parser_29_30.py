from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

URL = 'http://www.scrf.gov.ru/about/leadership/'
HOST = 'http://www.scrf.gov.ru'


def get_person(link):
    html_link = f.get_html(link)
    soup = BeautifulSoup(html_link.text, 'html.parser')
    item = soup.find('div', class_='profile')
    try:
        image_link = HOST + item.find('div', class_='profile-pic__img').find('img').get('src')
    except:
        image_link = '-'
    item = item.find('figcaption', class_='profile-pic__caption')
    name = item.find('dt').get_text()
    work = item.find('dd').get_text()
    work = f.get_work(work, 29)
    name = f.split_name(name, 2)
    try:
        item = soup.find('div', class_='l-col1').get_text()
        item = item[item.find('Родился') + len('Родился') + 1:item.find('.')-2]
        item = item.replace(chr(10), ' ')
        date = f.get_dig_date(item)
    except:
        date = {'day': 1, 'month': 1, 'year': 1901}
    return {'position_id': work, 'first_name': name[1], 'middle_name': name[2], 'last_name': name[0],
            'bday': date['day'], 'bmonth': date['month'], 'byear': date['year'], 'image_link': image_link, 'link': link}


def get_people(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    people = []
    try:
        items = soup.find_all('a', class_='person')
        for item in items:
            if not item.find('dd').get_text().find('помощник') != -1:
                links.append(HOST + item.get('href'))
        for link in links:
            people.append(get_person(link))
        return people
    except:
        return 1


def parser():
    log.debug(f"The script {__name__} starts working")
    people = []
    html = f.get_html(URL)
    if html.status_code == 200:
        people = get_people(html.text)
        if people == 1:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]
