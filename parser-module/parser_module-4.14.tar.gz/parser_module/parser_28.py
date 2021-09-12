from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

URL = 'https://sledcom.ru/sk_russia/leaders'
HOST = 'https://sledcom.ru'


def get_person(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find('div', class_='inner-page__list-item')
        name = f.get_name(item.find('a').get_text().lower())
        link = HOST + item.find('a').get('href')
        link_html = f.get_html(link)
        soup_link = BeautifulSoup(link_html.text, 'html.parser')
        item = soup_link.find('article', class_='direction-view')
        image_link = HOST + item.find('img').get('src')
        date = item.find('section', class_='collapsible__item')
        date = date.find('div', class_='collapsible__body').get_text()
        date = f.get_dig_date(date[date.find('родился ')+len('родился '): date.find('.')-2])
        return {'position_id': 28, 'first_name': name[1], 'middle_name': name[2], 'last_name': name[0],
                'bday': date['day'], 'bmonth': date['month'], 'byear': date['year'], 'image_link': image_link, 'link': link}
    except:
        return 1


def parser():
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(URL)
    person = []
    if html.status_code == 200:
        box = get_person(html.text)
        if box == 1:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
        person.append(box)
        log.debug("The script stops working")
        return person
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]
