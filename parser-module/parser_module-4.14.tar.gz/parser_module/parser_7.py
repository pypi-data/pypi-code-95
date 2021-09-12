import os
from bs4 import BeautifulSoup
from parser_libraries import functions as f
import logging
import logging.handlers

logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL = "https://ru.m.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D0%BD%D0%BE%D0%BC%D0%BE%D1%87%D0%BD%D1%8B%D0%B9_%D0%BF%D1%80%D0%B5%D0%B4%D1%81%D1%82%D0%B0%D0%B2%D0%B8%D1%82%D0%B5%D0%BB%D1%8C_%D0%BF%D1%80%D0%B5%D0%B7%D0%B8%D0%B4%D0%B5%D0%BD%D1%82%D0%B0_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B9_%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8_%D0%B2_%D1%84%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%BC_%D0%BE%D0%BA%D1%80%D1%83%D0%B3%D0%B5#:~:text=%D0%9F%D0%BE%D0%BB%D0%BD%D0%BE%D0%BC%D0%BE%D1%87%D0%BD%D1%8B%D0%B9%20%D0%BF%D1%80%D0%B5%D0%B4%D1%81%D1%82%D0%B0%D0%B2%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%20%D0%BF%D1%80%D0%B5%D0%B7%D0%B8%D0%B4%D0%B5%D0%BD%D1%82%D0%B0%20%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B9%20%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8%20%D0%B2%20%D1%84%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%BC%20%D0%BE%D0%BA%D1%80%D1%83%D0%B3%D0%B5%20%E2%80%94%20%D0%B4%D0%BE%D0%BB%D0%B6%D0%BD%D0%BE%D1%81%D1%82%D0%BD%D0%BE%D0%B5%20%D0%BB%D0%B8%D1%86%D0%BE,%D0%B3%D0%BB%D0%B0%D0%B2%D1%8B%20%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B0%20%D0%BD%D0%B0%20%D1%82%D0%B5%D1%80%D1%80%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D0%B8%20%D0%BE%D0%BA%D1%80%D1%83%D0%B3%D0%B0"
HOST = "https://ru.m.wikipedia.org"

def parser():
    log.debug(f"The script {__name__} starts working")
    people = []
    html = f.get_html(URL)
    if html.status_code == 200:
        try:
            soup = BeautifulSoup(html.text, 'html.parser')
            soup = soup.find('div', class_='content')
            soup = soup.find_all('section')
            soup = soup[3:-4]
            links = []
            for sou in soup:
                sou = sou.find('ul')
                sou = sou.find_all('li')
                sou = sou[-1]
                try:
                    link = sou.find('a').get('href')
                    links.append(HOST + link)
                except:
                    name = f.get_name(sou.find('a').get_text().lower().replace(',', ''))
                    person = {'image_link': "-",
                        'first_name': name[1],
                        'middle_name': name[2],
                        'last_name': name[0],
                        'link': URL,
                        'bday': 1,
                        'bmonth': 1,
                        'byear': 1901,
                        'position_id': 7}
                    people.append(
                        person
                    )
                if links[-1].find("edit") != -1:
                    name = f.get_name(sou.find('a').get_text().lower().replace(',', ''))
                    person = {'image_link': "-",
                              'first_name': name[1],
                              'middle_name': name[2],
                              'last_name': name[0],
                              'link': URL,
                              'bday': 1,
                              'bmonth': 1,
                              'byear': 1901,
                              'position_id': 7}
                    people.append(
                        person
                    )
                    links.pop()
            for link in links:
                html_cont = f.get_html(link)
                soup = BeautifulSoup(html_cont.text, 'html.parser')
                soup = soup.find('table', class_='infobox')
                name = soup.find('th', class_='infobox-above').get_text().lower().split()
                try:
                    image = "https:" + soup.find('td', class_='infobox-image').find('img').get('src')
                except:
                    image = '-'
                try:
                    date = f.get_dig_date(soup.find('span', class_='bday').get_text(), 2)
                except:
                    date = f.get_dig_date('01 01 1901')
                work = soup.find_all('tr')[3].get_text().lower()
                if work.find('заместитель председателя правительства') != -1:
                    work = 4
                else:
                    work = 7
                person1 = {
                    'image_link': image,
                    'first_name': name[0],
                    'middle_name': name[1],
                    'last_name': name[2],
                    'link': link,
                    'bday': date['day'],
                    'bmonth': date['month'],
                    'byear': date['year'],
                    'position_id': work
                }
                people.append(
                    person1
                )
            log.debug(f"The script stops working")
            return people
        except:
            print(people)
            return [{'code': 1, 'script': os.path.basename(__file__)}]
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]

if __name__ == "__main__":
    print(parser())
