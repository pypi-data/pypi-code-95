from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers
import json


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL = 'http://duma.gov.ru/data.json'
URL_COMMITTEE = 'http://duma.gov.ru/duma/commissions/'
HOST = 'http://duma.gov.ru'


def parser():
    people = []
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(URL)
    if html.status_code == 200:
        try:
            res = json.loads(html.text)
            res = res['persons']
            for person in res:
                flag = False
                try:
                    image = HOST + person['photo']
                except:
                    image = '-'
                url = HOST + person['url']
                if url.find('persons') != -1:
                    if url.find('staff') != -1:
                        flag = True
                    log.debug(f"Parsing {url}")
                    try:
                        person_html = f.get_html(url)
                        soup = BeautifulSoup(person_html.text, 'html.parser')
                        soup = soup.find('div', class_='content--s').get_text().lower()
                        soup = f.get_dig_date(soup[soup.find('рождения: ')+len('рождения: '):soup.find('года')])
                    except:
                        soup = f.get_dig_date('01 01 1901')
                    if soup == -1:
                        soup = f.get_dig_date('01 01 1901')
                    work = None
                    for pos in person['commission_positions']:
                        if pos['position_text'].find('член') != -1 and work != 19:
                            work = 20
                        else:
                            work = 19
                    if work == None:
                        flag = True
                    if not flag:
                        people.append(
                            {
                                'image_link': image,
                                'first_name': person['first_name'],
                                'middle_name': person['second_name'],
                                'last_name': person['last_name'],
                                'link': url,
                                'bday': soup['day'],
                                'bmonth': soup['month'],
                                'byear': soup['year'],
                                'position_id': work
                            }
                        )
            log.debug("The script stops working")
            return people
        except:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]


if __name__ == '__main__':
    print(parser())