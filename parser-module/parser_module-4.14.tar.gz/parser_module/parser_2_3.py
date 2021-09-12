import time
import os
from bs4 import BeautifulSoup
from parser_libraries import functions as f
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL = 'http://government.ru/gov/persons/'
HOST = 'http://government.ru'


def get_person(URL):
    try:
        people = []
        html = f.get_html(URL + 'bio')
        link = URL + 'bio'
        flag = False
        if html.status_code == 404:
            html = f.get_html(URL)
            link = URL
            flag = True
        soup = BeautifulSoup(html.text, 'html.parser')
        text = soup.find('div', class_='page_wrapper bio')
        if not text:
            flag = True
        name = f.get_name(soup.find('p', class_='vcard_name').get_text().lower())
        work = soup.find('p', class_='vcard_position').get_text().lower()
        image_link = soup.find('div', class_='vcard_photo').find('img').get('srcset')
        image_link = image_link[:-3]
        if not flag:
            text = text.find('p', class_='')
            text = text.find('p').get_text().lower()
            indl = text.find(' ')
            text = text[indl+1:text.find(' г')]
            date = f.get_dig_date(text)
            if date == -1:
                linking = 'https://ru.wikipedia.org/wiki/'
                nam = name[2][0].upper()+name[2][1:]+',_'+name[0][0].upper()+name[0][1:]+'_'+name[1][0].upper()+name[1][1:]
                for na in nam:
                    if na != '_' and na != ',':
                        strlist = f.get_base(ord(na), 2)
                        str1 = '110'+strlist[:5]
                        str2 = '10'+strlist[5:]
                        str1 = '%' + str(f.get_base(f.get_dec(int(str1),2),16)).upper()
                        str2 = '%' + str(f.get_base(f.get_dec(int(str2),2),16)).upper()
                        linking += str1+str2
                    else:
                        linking += na
                html2 = f.get_html(linking)
                try:
                    date_soup = BeautifulSoup(html2.text, 'html.parser')
                    date_soup = date_soup.find('span', class_='bday').get_text()
                    date = f.get_dig_date(date_soup, 2)
                except: date = {"year": 1901, "day": 1, "month": 1}
        else:
            linking = 'https://ru.wikipedia.org/wiki/'
            nam = name[2][0].upper()+name[2][1:]+',_'+name[0][0].upper()+name[0][1:]+'_'+name[1][0].upper()+name[1][1:]
            for na in nam:
                if na != '_' and na != ',':
                    strlist = f.get_base(ord(na), 2)
                    str1 = '110'+strlist[:5]
                    str2 = '10'+strlist[5:]
                    str1 = '%' + str(f.get_base(f.get_dec(int(str1),2),16)).upper()
                    str2 = '%' + str(f.get_base(f.get_dec(int(str2),2),16)).upper()
                    linking += str1+str2
                else:
                    linking += na
            html2 = f.get_html(linking)
            try:
                date_soup = BeautifulSoup(html2.text, 'html.parser')
                date_soup = date_soup.find('span', class_='bday').get_text()
                date = f.get_dig_date(date_soup, 2)
            except:
                date = {"year": 1901, "day": 1, "month": 1}
        work = f.get_work(work, 2)
        try:
            a = work[1]
            people.append({
                    'image_link': image_link,
                    'first_name': name[0],
                    'middle_name': name[1],
                    'last_name': name[2],
                    'link': link,
                    'bday': date['day'],
                    'bmonth': date['month'],
                    'byear': date['year'],
                    'position_id': a
                 }
            )
            people.append({
                'image_link': image_link,
                'first_name': name[0],
                'middle_name': name[1],
                'last_name': name[2],
                'link': link,
                'bday': date['day'],
                'bmonth': date['month'],
                'byear': date['year'],
                'position_id': work[0]
            }
            )
        except:
            people.append({
                'image_link': image_link,
                'first_name': name[0],
                'middle_name': name[1],
                'last_name': name[2],
                'link': link,
                'bday': date['day'],
                'bmonth': date['month'],
                'byear': date['year'],
                'position_id': work
                }
            )
        return people
    except:
        return 1


def parser():
    log.debug(f"The script {__name__} starts working")
    people = []
    html = f.get_html(URL)
    if html.status_code == 200:
        time.sleep(5)
        soup = BeautifulSoup(html.text, 'html.parser')
        list = soup.find_all('li', class_='person')
        for pos in list:
            box = get_person(HOST + pos.find('a', class_='person_slide').get('href'))
            if box == 1:
                return [{'code': 1, 'script': os.path.basename(__file__)}]
            people.extend(box)
            time.sleep(0.1)
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]


if __name__ == "__main__":
    print(parser())