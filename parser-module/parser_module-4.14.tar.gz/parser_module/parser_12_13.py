from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

URL= 'http://council.gov.ru/structure/administration/'
HOST = 'http://council.gov.ru'


def parser():
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(URL)
    if html.status_code == 200:
        try:
            soup = BeautifulSoup(html.text, 'html.parser')
            contents = soup.find_all('div', class_='senator__person senator__person_medium')
            people = []
            for content in contents:
                link = content.find('a').get('href')
                if link.find('http'):
                    link = HOST + link
                image_link = content.find('img').get('srcset')
                image_link = image_link[0:-3]
                name = f.get_name(content.find('img').get('alt').lower())
                work = content.find('a', class_='senators_title').get('title').lower()
                if work.find('заместител') != -1:
                    work = 13
                else:
                    work = 12
                date = content.find('div', class_='person_info_private tooltip__wrapper').get_text().lower()
                date = date[date.find(': ')+2:date.find('года')]
                date = f.get_dig_date(date)
                people.append({
                    'image_link': image_link,
                    'first_name': name[1],
                    'middle_name': name[2],
                    'last_name': name[0],
                    'link': link,
                    'bday': date['day'],
                    'bmonth': date['month'],
                    'byear': date['year'],
                    'position_id': work
                })
            log.debug("The script stops working")
            return people
        except:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]
