import os
from parser_libraries import functions as f
from bs4 import BeautifulSoup
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL_1 = "http://www.cdep.ru/index.php?id=32"
URL_2 = "http://viperson.ru/search?query="
HOST = "http://viperson.ru"


def get_person(html):
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find('div', class_="contentBody customArea").find_next('span').get_text().lower()
    name = f.get_name(name)
    return name


def get_content(URL, name):
    search = f.get_html(URL)
    if search.status_code == 200:
        soup = BeautifulSoup(search.text, 'html.parser')
        href = soup.find('table', class_='pi-sup__table').find_next('td', class_='pi-sup__img-td').find_next('a', class_='pi-sup__img-box').get('href')
        link = HOST + href
        html = f.get_html(link)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'html.parser')
            image_link = HOST + soup.find('div', class_='wrap').find_next('div', class_='prsn__box group').find_next('img', class_='prsn__img').get('src')
            position_id = 45
            b_date = soup.find('div', class_='wrap').find_next('div', class_='prsn__box group').find_next('div', class_='prsn__descr').find_next('div', class_='prsn__live').text
            b_date = f.get_dig_date(b_date.replace('года', ''))
            person = {
                'image_link': image_link,
                'first_name': name[0],
                'middle_name': name[1],
                'last_name': name[2],
                'link': link,
                'bday': b_date['day'],
                'bmonth': b_date['month'],
                'byear': b_date['year'],
                'position_id': position_id
            }
            return person
        else:
            return [{'code': 2, 'script': os.path.basename(__file__)}]
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]


def parser():
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(URL_1)
    people = []
    if html.status_code == 200:
        name = get_person(html.text)
        URL = URL_2
        for i in range(len(name)):
            URL += name[i] + "+"
        URL = URL[:-1]
        person = get_content(URL, name)
        people.append(person)
        if people == 1:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]