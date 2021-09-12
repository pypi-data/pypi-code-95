from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

host = 'http://www.arbitr.ru'
url = host+'/as/'
addition = 'about/ourJudges/'
addition_kr = 'kasyanova'


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def parser_person(link, wbsite):
    try:
        html = f.get_html(link["link"])
        soup = BeautifulSoup(html.text, 'html.parser')
        soup = soup.find('div', class_='b-content-body js-content-body')
        try:
            image_link = wbsite[:-1] + soup.find('img').get('src')
        except:
            image_link = '-'
        name = soup.find('div', class_='b-card-title-container')
        work = name.find('h3', class_='b-card-title b-card-post').get_text().lower()
        name = name.find('h2').get_text().replace('.', ' ')
        if name == "" or name == None:
            name = link["name"].replace(".", " ")
        name = f.get_name(name)
        date = soup.find_all('dl', class_='b-card-info-block g-clrfix')
        try:
            date = date[-1].get_text().lower()
            if date.find('родился') != -1:
                year = date.find('года')
                if year != -1:
                    date = date[date.find('родился')+len('родился'):year]
                elif date.find('г.') != -1:
                    date = date[date.find('родился')+len('родился'):date.find('г.')]
            elif date.find('родилась') != -1:
                year = date.find('года')
                if year != -1:
                    date = date[date.find('родилась') + len('родилась'):year]
                elif date.find('г.') != -1:
                    date = date[date.find('родилась') + len('родилась'):date.find('г.')]
            else:
                date = date[date.find('.')-2:date.find('.')+8]
            date = date.replace('.', ' ')
            date = f.get_dig_date(date)
        except:
            date = -1
        lst = {}
        if date == -1 or date['year'] > 2000:
            lst = {
            'image_link': image_link,
            'first_name': name[1],
            'middle_name': name[2],
            'last_name': name[0],
            'link': link["link"],
            'bday': 1,
            'bmonth': 1,
            'byear': 1901,
            'position_id': f.get_work(work, 42),
            }
        else:
            lst = {
            'image_link': image_link,
            'first_name': name[1],
            'middle_name': name[2],
            'last_name': name[0],
            'link': link["link"],
            'bday': date['day'],
            'bmonth': date['month'],
            'byear': date['year'],
            'position_id': f.get_work(work, 42),
            }
        return lst
    except:
        return 1


def parser_people_links(link):
    links = []
    if link.find('krasnoyarsk') != -1:
        html = f.get_html(link+addition+addition_kr)
    else:
        html = f.get_html(link+addition)
    if html.status_code == 503:
        log.warning("Server offline, skipping")
        return None
    soup = BeautifulSoup(html.text, 'html.parser')
    soup = soup.find('div', class_='l-columns')
    if soup != None:
        soup = soup.find('div', class_='l-column l-column--left js-column')
        try:
            soup1 = soup.find('ul', class_='b-menu js-menu menu')
            soup4 = soup1.find('li', class_='b-menu-item--active')
            try:
                soup4 = soup4.find('div', class_='b-submenu js-submenu b-submenu--all')
                soup1 = soup4
            except:
                soup1 = soup1.find("div", class_="b-menu-item js-menu-item b-menu-item--active js-menu-item--active b-menu-item--is_submenu")
                soup1 = soup1.find('div', class_='b-submenu js-submenu b-submenu--all')
            soup1 = soup1.find('ul', class_='b-menu js-menu menu')
            soup1 = soup1.find_all('li')
        except:
            try:
                soup3 = soup.find_all('ul', class_='b-menu js-menu menu accordion')
                soup3 = soup3[3]
                soup1 = soup3.find_all('li')
            except:
                try:
                    soup2 = soup.find('ul', class_='b-menu js-menu menu accordion')
                    soup2 = soup2.find('li', class_='b-menu-item js-menu-item b-menu-item--active js-menu-item--active b-menu-item--is_submenu')
                    soup2 = soup2.find('div', class_='b-submenu js-submenu b-submenu--accordion')
                    soup2 = soup2.find('ul', class_='b-menu js-menu menu accordion')
                    soup1 = soup2.find_all('li')
                except:
                    soup3 = soup.find('ul', class_='b-menu js-menu menu ')
                    soup3 = soup3.find('li', class_= 'b-menu-item js-menu-item b-menu-item--active js-menu-item--active b-menu-item--is_submenu first')
                    soup3 = soup3.find('div', class_='b-submenu js-submenu b-submenu--all')
                    soup3 = soup3.find('ul', class_='b-menu js-menu menu ')
                    soup1 = soup3.find_all('li')
        for sou in soup1:
            sou = sou.find('a', class_='item_link')
            if sou != None:
                if sou.get('href').find(".ru") == -1:
                    links.append({"link":link[:-1] + sou.get('href'), "name": sou.get_text()})
                else:
                    if sou.get('href').find("http") == -1:
                        links.append({"link": "http:/" + sou.get('href'), "name": sou.get_text()})
                    else:
                        links.append({"link": sou.get('href'), "name": sou.get_text()})
    else:
        links = None
    return links


def parser_direct_link(link):
    html = f.get_html(link)
    soup = BeautifulSoup(html.text, 'html.parser')
    soup = soup.find_all('table', cellpadding='5')
    try:
        soup = soup[-1]
    except:
        pass
    soup = soup.find_all('a')
    soup = soup[-1].get('href')
    return soup


def parser_website(link):
    links = []
    html = f.get_html(link)
    soup = BeautifulSoup(html.text, 'html.parser')
    soup = soup.find_all('a', class_='zag21')
    for sou in soup:
        links.append(host + sou.get('href'))
    return links


def get_orenburg():
    links = []
    people = []
    log.debug(f'Parsing https://orenburg.arbitr.ru/')
    html = f.get_html('https://orenburg.arbitr.ru/about/ourJudges/aleksandrov')
    soup = BeautifulSoup(html.text, 'html.parser')
    soup = soup.find('div', class_='l-columns')
    soup = soup.find('div', class_='l-column l-column--left js-column')
    soup = soup.find('ul', class_='b-menu js-menu menu')
    soup = soup.find('div', class_='b-submenu js-submenu b-submenu--all')
    soup = soup.find('ul', class_='b-menu js-menu menu')
    soup = soup.find_all('li')
    for sou in soup:
        sou = sou.find('a', class_='item_link')
        if sou != None:
            links.append({"link":'https://orenburg.arbitr.ru' + sou.get('href'), "name": sou.get_text()})
    for link in links:
        people.append(parser_person(link, 'https://orenburg.arbitr.ru/'))
    return people

def parser_irk(link):
    people = []
    html_irk_1 = f.get_html(link)
    soup_irk_1 = BeautifulSoup(html_irk_1.text, "html.parser")
    soup_irk_1 = soup_irk_1.find("div", class_="single")
    soup_irk_1 = soup_irk_1.find_all("a")
    for syd in soup_irk_1:
        html_syd = f.get_html(syd.get("href"))
        soup_irk_syd = BeautifulSoup(html_syd.text, "html.parser")
        soup_irk_syd = soup_irk_syd.find("div", class_="single")
        soup_irk_syd = soup_irk_syd.find_all("a")
        for sou in soup_irk_syd:
            name = sou.get_text()
            name = name.split()
            work = 44
            if len(name) > 3:
                work = 42
                name = name[4:]
            people.append({
                'image_link': "-",
                'first_name': name[1],
                'middle_name': name[2],
                'last_name': name[0],
                'link': sou.get("href"),
                'bday': 1,
                'bmonth': 1,
                'byear': 1901,
                'position_id': work,
            })
    return people

def parser():
    log.debug(f"The script {__name__} starts working")
    links = []
    people = []

    html = f.get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        soup = soup.find_all(class_='menu2')
        for sou in soup:
            links.append(host+sou.get('href'))
        for link in links:
            website_links = parser_website(link)
            for website_link in website_links:
                direct_link = parser_direct_link(website_link)+'/'
                log.debug(f'Parsing {direct_link}')
                i = 0
                while i<3:
                    try:
                        people_links = parser_people_links(direct_link)
                        i=4
                    except:
                        if i == 2:
                            if direct_link.find('perm') != -1 :
                                pass
                            elif direct_link.find('orenburg') != -1:
                                pass
                            else:
                                return [{'code': 1, 'script': os.path.basename(__file__)}]

                        people_links = None
                        i+=1
                        log.warning(f'Duplicate or non-templated html at -> {direct_link}')
                if people_links != None:
                    for person_link in people_links:
                        if person_link != None:
                            person = parser_person(person_link, direct_link)
                            if person != 1:
                                people.append(person)
                            else:
                                return [{'code': 1, 'script': os.path.basename(__file__)}]
        log.debug('Parsing https://ipc.arbitr.ru/')
        people_links = parser_people_links('https://ipc.arbitr.ru/')
        for person_link in people_links:
            if person_link != None:
                person = parser_person(person_link, 'https://ipc.arbitr.ru/')
                if person != 1:
                    people.append(person)
        people.extend(get_orenburg())


        html_tver = f.get_html("https://tver.arbitr.ru/node/3515")
        soup_tver = BeautifulSoup(html_tver.text, "html.parser")
        soup_tver = soup_tver.find("div", class_="node")
        tver_list = soup_tver.find_all("p")
        tver_list = tver_list[1:]
        for item in tver_list:
            try:
                name = item.find("strong").get_text().replace("\n", "")
                name = f.get_name(name)
                people.append({
                    'image_link': "-",
                    'first_name': name[1],
                    'middle_name': name[2],
                    'last_name': name[0],
                    'link': "https://tver.arbitr.ru/node/3515",
                    'bday': 1,
                    'bmonth': 1,
                    'byear': 1901,
                    'position_id': 44,
                })
            except:
                pass

        html_fasvso = f.get_html("http://fasvso.arbitr.ru/about/struktura_suda/svedeniya_o_sud_yah/")
        soup_fasvso = BeautifulSoup(html_fasvso.text, "html.parser")
        soup_fasvso = soup_fasvso.find('div', class_="evaldyarticles")
        soup_fasvso = soup_fasvso.find_all("div")
        for item in soup_fasvso:
            li = "http://fasvso.arbitr.ru" + item.find("a").get("href")
            name = item.get_text().lower().replace("\n", "")
            name = f.get_name(name)
            people.append({
                'image_link': "-",
                'first_name': name[1],
                'middle_name': name[2],
                'last_name': name[0],
                'link': li,
                'bday': 1,
                'bmonth': 1,
                'byear': 1901,
                'position_id': 44,
            })

        html_irk = f.get_html(
            "https://irkutsk.arbitr.ru/o-sude/struktura-suda/sudi/predsedatel-arbitrazhnogo-suda-irkutskoj-oblasti/")
        soup_irk = BeautifulSoup(html_irk.text, "html.parser")
        soup_irk = soup_irk.find("div", class_="single")
        im = soup_irk.find("strong")
        name = im.get_text()
        name = f.get_name(name)
        soup_irk = soup_irk.find_all("p")
        date = soup_irk[2].get_text().lower()
        if date.find('родился') != -1:
            year = date.find('года')
            if year != -1:
                date = date[date.find('родился') + len('родился'):year]
            elif date.find('г.') != -1:
                date = date[date.find('родился') + len('родился'):date.find('г.')]
        elif date.find('родилась') != -1:
            year = date.find('года')
            if year != -1:
                date = date[date.find('родилась') + len('родилась'):year]
            elif date.find('г.') != -1:
                date = date[date.find('родилась') + len('родилась'):date.find('г.')]
        else:
            date = date[date.find('.') - 2:date.find('.') + 8]
        date = date.replace('.', ' ')
        date = f.get_dig_date(date)

        people.append({
            'image_link': im.find("a").get("href"),
            'first_name': name[0],
            'middle_name': name[1],
            'last_name': name[2],
            'link': "https://irkutsk.arbitr.ru/o-sude/struktura-suda/sudi/predsedatel-arbitrazhnogo-suda-irkutskoj-oblasti",
            'bday': date["day"],
            'bmonth': date["month"],
            'byear': date["year"],
            'position_id': 42,
        })

        people.extend(parser_irk(
            "https://irkutsk.arbitr.ru/o-sude/struktura-suda/sudi/sudebnaya-kollegiya-po-rassmotreniyu-sporov-voznikayushhih-iz-administrativnyh-i-inyh-publichnyh-pravootnoshenij/"))
        people.extend(parser_irk(
            "https://irkutsk.arbitr.ru/o-sude/struktura-suda/sudi/sudebnaya-kollegiya-po-rassmotreniyu-sporov-voznikayushhih-iz-grazhdanskih-i-inyh-pravootnoshenij/"))

        log.debug("The script stops working")
        return people
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]

if __name__ == '__main__':
    print(parser())