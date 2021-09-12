import os
from parser_libraries import functions as f
from bs4 import BeautifulSoup
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

URL = 'http://www.cikrf.ru/about/'
HOST = 'http://www.cikrf.ru'


def get_person(html):
    try:
        link_html = f.get_html(html['link'])
        soup = BeautifulSoup(link_html.text, 'html.parser')
        name = f.get_name(soup.find('span', class_='name').get_text().lower())
        image_link = HOST + soup.find('div', class_='col-xs-12 col-sm-4 col-md-3 img').find('img').get('src')
        date = soup.find('p').get_text()
        date = f.get_dig_date(date[date.find(' ')+1:date.find(' года')])
        return {
            'image_link': image_link,
            'first_name': name[1],
            'middle_name': name[2],
            'last_name': name[0],
            'link': html['link'],
            'bday': date['day'],
            'bmonth': date['month'],
            'byear': date['year'],
            'position_id': html['work']
        }
    except:
        return 1


def parser():
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(URL)
    links = []
    people = []
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find('div', class_='content_body')
        items = items.find('div', class_='row')
        items = items.find_all('div', class_='election_committee_item col-xs-6 col-md-4')
        for item in items:
            text = item.find('script')
            if text != None:
                text.get_text()
                if text.find('none'):
                    continue
            else:
                links.append({'link': HOST + item.find('a').get('href'), 'work': f.get_work(item.find('span', class_='position').get_text(), mode=38)})
        for link in links:
            box = get_person(link)
            if box == 1:
                return [{'code': 1, 'script': os.path.basename(__file__)}]
            people.append(box)
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]
