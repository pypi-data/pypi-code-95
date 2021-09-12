from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import time
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL = 'http://council.gov.ru/structure/committees/'


def get_people(html):
    people = []
    links = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        soup = soup.find('div', class_='wrapper')
        links.append({'link': soup.find('div', class_='senator__person senator__person_medium').find('a').get('href'), 'work': 14})
        firsts = soup.find_all('div', class_='first_deputy_chairman')
        for first in firsts:
            links.append({'link': first.find('a').get('href'), 'work': 14})
        seconds = soup.find_all('div', class_='deputy_chairmen')
        for second in seconds:
            links.append({'link': second.find('a').get('href'), 'work': 14})
        lasts = soup.find_all('div', class_='deputy_members col_4 col')
        lasts.extend(soup.find_all('div', class_='deputy_members col_4 col col_last'))
        for last in lasts:
            links.append({'link': last.find('a').get('href'), 'work': 15})
        i = 1
        for link in links:
            log.debug(str(i) + '/' + str(len(links)))
            link_html = f.get_html(link['link'])
            link_soup = BeautifulSoup(link_html.text, 'html.parser')
            name = f.get_name(link_soup.find('h2', class_='senators_title').get_text().lower())
            try:
                image_link = link_soup.find('img', class_='person_img').get('srcset')
                image_link = image_link[:image_link.find(' 2x')]
            except:
                image_link = "-"
            date = link_soup.find('p').get_text()
            date = f.get_dig_date(date[date.find(': ')+2:date.find(' года')])
            people.append({
                'image_link': image_link,
                'first_name': name[1],
                'middle_name': name[2],
                'last_name': name[0],
                'link': link['link'],
                'bday': date['day'],
                'bmonth': date['month'],
                'byear': date['year'],
                'position_id': link['work']
            })
            time.sleep(0.5)
            i += 1
        log.debug("The script stops working")
        return people
    except:
        return 1


def parser():
    log.debug(f"The script {__name__} starts working")
    people = []
    html = f.get_html(URL)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('div', class_='block__department')
        i = 1
        for item in items:
            log.debug('Page ' + str(i) + '/' + str(len(items)))
            link = item.find('a').get('href')
            link_html = f.get_html(link)
            box = get_people(link_html.text)
            if box == 1:
                return ({'code': 1, 'script': os.path.basename(__file__)})
            people.extend(box)
            i += 1
        return people
    else:
        return ({'code': 2, 'script': os.path.basename(__file__)})

if __name__ == '__main__':
    print(parser())