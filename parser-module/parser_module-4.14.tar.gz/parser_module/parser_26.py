from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL_1 = "http://supcourt.ru/about/structure/220/"
URL_2 = "http://supcourt.ru/about/structure/221/"
URL_3 = "http://supcourt.ru/about/structure/222/"
URL_4 = "http://supcourt.ru/about/structure/223/"
HOST = "http://supcourt.ru"


def get_links(url):
    links = []
    people = []
    html = f.get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, "html.parser")
        soup = soup.find('div', class_='vs-structure')
        soup = soup.find_all('div', class_='clearfix')
        for sou in soup:
            try:
                links.append(HOST + sou.find('a').get('href'))
            except:
                sou = sou.find('div', class_='vs-text').find('h2').get_text().lower()
                name = f.get_name(sou)
                people.append(
                    {
                        'image_link': "-",
                        'first_name': name[1],
                        'middle_name': name[2],
                        'last_name': name[0],
                        'link': url,
                        'bday': 1,
                        'bmonth': 1,
                        'byear': 1901,
                        'position_id': 26
                    }
                )
        for link in links:
            person = get_person(link)
            if person != 1:
                people.append(person)
            else:
                return 1
        return people
    else:
        return 1


def get_person(link):
    html = f.get_html(link)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        soup = soup.find_all('div', class_='vs-inner clearfix')
        soup = soup[-2]
        name = f.get_name(soup.find('div', class_='vs-grid-medium').get_text().replace('\n', '').lower())
        try:
            image_link = HOST + soup.find('img').get('src')
        except:
            image_link = "-"
        try:
            date = soup.get_text().lower()
            if date.find('родился') != -1:
                if date.find('год') != -1:
                    date = f.get_dig_date(date[date.find('родился')+len('родился'): date.find('год')])
                else:
                    date = f.get_dig_date(date[date.find('родился') + len('родился'): date.find('г.')])
            elif date.find('родилась') != -1:
                if date.find('год') != -1:
                    date = f.get_dig_date(date[date.find('родилась')+len('родилась'): date.find('год')])
                else:
                    date = f.get_dig_date(date[date.find('родилась') + len('родилась'): date.find('г.')])
        except:
            date = f.get_dig_date("01 01 1901")
        if date == -1:
            date = f.get_dig_date("01 01 1901")
        if type(date) != type({}):
            date = f.get_dig_date("01 01 1901")
        return {
            'image_link': image_link,
            'first_name': name[1],
            'middle_name': name[2],
            'last_name': name[0],
            'link': link,
            'bday': date['day'],
            'bmonth': date['month'],
            'byear': date['year'],
            'position_id': 26
        }
    else:
        return 1


def parser():
    log.debug(f"The script {__name__} starts working")
    people = []
    ar = get_links(URL_1)
    if ar != 1:
        people.extend(ar)
    else:
        return [{'code': 1, 'script': os.path.basename(__file__)}]

    ar = get_links(URL_2)
    if ar != 1:
        people.extend(ar)

    else:
        return [{'code': 1, 'script': os.path.basename(__file__)}]

    ar = get_links(URL_3)
    if ar != 1:
        people.extend(ar)
    else:
        return [{'code': 1, 'script': os.path.basename(__file__)}]

    html = f.get_html(URL_4)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        links = soup.find_all('h1', class_='vs-structure-list-section')
        for link in links:
            link = link.find('a').get('href')
            ar = get_links(HOST+link)
            if ar != 1:
                people.extend(ar)
            else:
                return [{'code': 1, 'script': os.path.basename(__file__)}]
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]
    log.debug("The script stops working")
    return people