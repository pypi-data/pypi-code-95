from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import time
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


URL_COMMITTEE = 'http://www.gosduma.net/structure/committees/'
HOST = 'http://www.gosduma.net'

def get_links(html):
    links = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='section-line')
    for item in items:
        item = item.find('div', class_='table-data td-filter')
        links.extend(item.find_all('tr'))
    links_real = []
    for link in links:
        if link.find('td'):
            link = link.find('td')
            links_real.append(HOST + link.find('a').get('href'))
    return links_real


def get_data(html, name):
    soup = BeautifulSoup(html, 'html.parser')
    item = []
    if soup.find('p', class_='deputat-info-date'):
        item.append(soup.find('p', class_='deputat-info-date').get_text().replace('Дата рождения: ', ''))
    else:
        item.append('-')
    soup = soup.find('div', class_='deputat-info-left')
    if soup.find('img'):
        item.append(HOST + soup.find('img').get('src'))
    else:
        linking = 'https://ru.wikipedia.org/wiki/'
        name = f.get_name(name)
        nam = name[0][0].upper() + name[0][1:] + ',_' + name[1][0].upper() + name[1][1:] + '_' + name[2][0].upper() + name[2][1:]
        for na in nam:
            if na != '_' and na != ',':
                strlist = f.get_base(ord(na), 2)
                str1 = '110' + strlist[:5]
                str2 = '10' + strlist[5:]
                str1 = '%' + str(f.get_base(f.get_dec(int(str1), 2), 16)).upper()
                str2 = '%' + str(f.get_base(f.get_dec(int(str2), 2), 16)).upper()
                linking += str1 + str2
            else:
                linking += na
        image_html = f.get_html(linking)
        soup_3 = BeautifulSoup(image_html.text, 'html.parser')
        soup_3 = soup_3.find('table', class_='infobox')
        link = soup_3.find('img')
        link = link.get('srcset')
        link = link[link.rfind('//'):link.find(' 2x')]
        item.append(link)
    return item


def get_people(html):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('div', class_='table-data td-filter'):
        items = soup.find('div', class_='table-data td-filter')
        items = items.find_all('tr')
        count = 1
        flag = True
        people = []
        for item in items:
            log.debug(str(count) + '/' + str(len(items)))
            if item.find('td'):
                data = []
                work = item.find_all('td')
                work = work[-1]
                work = work.get_text().lower()
                link = HOST + item.find('a').get('href')
                name = item.find('a').get('title').lower()
                data = get_data(f.get_html(link).text, name)
                data[0] = data[0].replace('года', '')
                name = f.get_name(name)
                list_data = f.get_dig_date(data[0])
                people.append({
                    'image_link': data[1],
                    'first_name': name[1],
                    'middle_name': name[2],
                    'last_name': name[0],
                    'link': link,
                    'bday': list_data['day'],
                    'bmonth': list_data['month'],
                    'byear': list_data['year'],
                    'position_id': f.get_work(work, 19)
                })
            count = count + 1
    else:
        people = -1
    return people


def parser():
    log.debug(f"The script {__name__} starts working")
    html_links = f.get_html(URL_COMMITTEE)
    if html_links.status_code == 200:
        links = get_links(html_links.text)
        people = []
        for j in range(0, len(links)+1):
            try:
                log.debug('Page ' + str(j) + '/' + str(len(links)))
                html_committee = f.get_html(links[j])
                people_list = get_people(html_committee.text)
                if people_list != -1:
                    people.extend(people_list)
            except:
                j -= 1
            time.sleep(1)
        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]
