from parser_libraries import functions as f
import os
from bs4 import BeautifulSoup
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL = 'http://duma.gov.ru/duma/structure/'
HOST = 'http://duma.gov.ru'


def get_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('section', class_='section section--embedded mobile-no-padding')
    links = []
    people = []
    for item in items:
        info = item.find_all('a', class_='object object--fractions link link--color')
        if info:
            for inf in info:
                chairman = f.get_html(HOST + inf.get('href') + 'chairman')
                soup_for_chairman = BeautifulSoup(chairman.text, 'html.parser')
                lk = soup_for_chairman.find('div', class_='person__content person__content--right')
                links.append(HOST + lk.find('a').get('href'))
        else:
            data = item.find_all('div', class_='person person--s')
            for dat in data:
                links.append(HOST + dat.find('a').get('href'))
    return links


def get_person(html):
    try:
        link = f.get_html(html)
        soup = BeautifulSoup(link.text, 'html.parser')
        postfix = '--mobile'
        if not soup.find('div', class_=('person person'+postfix)):
            postfix = '--l'
        item = soup.find('div', class_=('person person'+postfix))
        image = item.find('picture')
        image = item.find('img')
        image_link = HOST + image.get('src')
        item = item.find('div', class_='person__content person__content'+postfix)
        name = item.find('h2', class_='person__title person__title'+postfix).get_text()
        name = f.split_name(name)
        if postfix == '--l':
            work = item.find('p', class_='person__position person__position' + postfix).get_text()
        else:
            work = item.find('div', class_='person__position person__position--wide')
            work = work.find('div')
            work = work.find('a').get_text()
        work = f.get_work(work, mode=16)
        date = soup.find('div', class_='content--s')
        date = date.find('div', class_='text').get_text()
        date = date[date.find(': ')+1:date.find('года')]
        date = f.get_dig_date(date)
        return {'position_id': work, 'first_name': name[1], 'middle_name': name[2], 'last_name': name[0], 'bday': date['day'], 'bmonth': date['month'], 'byear': date['year'], 'image_link': image_link, 'link': html}
    except:
        return 1



def parser():
    log.debug(f"The script {__name__} starts working")
    people = []
    html = f.get_html(URL)
    if html.status_code == 200:
        links = get_links(html.text)
        for link in links:
            box = get_person(link)
            if box == 1:
                return [{'code': 1, 'script': os.path.basename(__file__)}]
            people.append(box)
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]