from parser_libraries import functions as f
from parser_libraries import SQL as SQL
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers


COMPLEX_URL = 'https://ru.wikipedia.org/wiki/%D0%A1%D1%83%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D1%8B_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B9_%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8'
HOST = 'https://ru.wikipedia.org/'


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_yandex_image(name):
    info = SQL.get_con_info()
    link = 'https://yandex.ru/images/search?text=' + name[0] + '%20' + name[1] + '%20' + name[2]
    html = f.get_selenium_html(link, chromium=info['chromium_path'], driver=info['chromedriver_path'], params=info['use_chromium'])
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('a', class_='serp-item__link')
    soup = soup.find('img').get('src')
    return soup


def get_wiki_person(link, work_id):
    html = f.get_html(link)
    soup = BeautifulSoup(html.text, 'html.parser')
    full_name = soup.find('h1', class_='firstHeading').get_text().lower().replace(',', '')
    if full_name.find('(') != -1:
        full_name = full_name[:full_name.find('(')]
    full_name = f.get_name(full_name)
    soup = soup.find('table', class_='infobox')
    try:
        image_link = soup.find('td', class_='infobox-image').find('img').get('srcset')
        if image_link != None:
            image_link = 'https:' + image_link[image_link.rfind(', ')+2:image_link.find(' 2x')]
        else:
            image_link = 'https:' + soup.find('td', class_='infobox-image').find('img').get('src')
    except:
        image_link = 'https:/' + get_yandex_image(full_name)
        image_link = image_link.replace(' ', '')
        image_link = image_link.replace('///', '//')
    soup = soup.find('span', class_='bday').get_text()
    if soup != None:
        date = f.get_dig_date(soup, 2)
    else:
        date = f.get_dig_date('01 01 1901')
    return {'position_id': work_id, 'first_name': full_name[1], 'middle_name': full_name[2], 'last_name': full_name[0],
            'bday': date['day'], 'bmonth': date['month'], 'byear': date['year'], 'image_link': image_link, 'link': link}


def get_page(link):
    people = []
    html = f.get_html(link)
    soup = BeautifulSoup(html.text, 'html.parser')
    soup = soup.find('table', class_='infobox')
    soup = soup.find_all('tr')
    for a in soup:
        try:
            cont = a.find('th', class_='plainlist').get_text().lower()
            if cont != None:
                if cont.find('губернатор') != -1 or cont.find('председатель') != -1 or cont.find('мэр') != -1  or cont.find('премьер-министр') != -1 or cont.find('глава') != -1:
                    name = a.find('td').get_text()
                    if name.find('[') != -1:
                        name = name[:name.find('[')]
                    elif name.find('(') != -1:
                        name = name[:name.find('(')]
                    title = a.find('td').find('a').get('title')
                    if title.find('страница отсутствует') == -1:
                        person_link = a.find('td').find('a').get('href')
                        people.append(get_wiki_person(HOST + person_link, 33))
                    else:
                        title = title.replace(' (страница отсутствует)', '')
                        if title.find('(') != -1:
                            title = title[:title.find('(')]
                        if title.rfind(' ') == len(title) - 1:
                            title = title[:-1]
                        full_name = [title[:title.find(',')].lower(), title[title.find(',')+1:title.rfind(' ')].lower(), title[title.rfind(' ')+1:].lower()]
                        for part in full_name:
                            part = part.replace(' ', '')
                        image_link = 'https:' + get_yandex_image(full_name)
                        image_link = image_link.replace(' ', '')
                        image_link = image_link.replace('///', '//')
                        people.append({
                                       'position_id': 33,
                                       'first_name': full_name[1],
                                       'middle_name': full_name[2],
                                       'last_name': full_name[0],
                                       'bday': 1,
                                       'bmonth': 1,
                                       'byear': 1901,
                                       'image_link': image_link,
                                       'link': link
                                       }
                                      )
        except:
            continue
    return people


def parser():
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(COMPLEX_URL)
    soup = BeautifulSoup(html.text, 'html.parser')
    links = []
    people = []
    soup = soup.find('table', class_='standard')
    prob = soup.find_all('tr', class_='dark')
    soup = soup.find_all('tr')
    soup = soup[2:-1]
    for a in soup:
        flag = True
        for b in prob:
            if a == b:
                flag = False
        if flag:
            links.append(HOST + a.find('a').get('href'))
    i = 1
    for link in links:
        log.debug(f'{i}/{len(links)+1}')
        i += 1
        a = get_page(link)
        people.extend(a)
    log.debug("The script stops working")
    return people
