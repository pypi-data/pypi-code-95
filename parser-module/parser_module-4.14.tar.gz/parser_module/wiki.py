import os
from parser_libraries import functions as f
from bs4 import BeautifulSoup
import logging
import logging.handlers
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


HOST = 'https://ru.wikipedia.org'


def get_content(html, cont_id, cont_work_id):
    try:
        soup = BeautifulSoup(html.text, 'html.parser')
        table = soup.find('table', class_='infobox')
        if cont_id == 1:
            work = table.find('th').get_text().lower()
            work = f.get_work(work)
            image_box = table.find_all('td', class_='infobox-image')
            image_box = image_box[-1]
            p_link = HOST + image_box.find('span', class_='no-wikidata').find('a').get('href')
        else:
            lists = table.find_all('tr')
            content = lists[cont_id-1]
            work = cont_work_id
            p_link = HOST + content.find('td').find('a').get('href')
        p_soup = BeautifulSoup(f.get_html(p_link).text, 'html.parser')
        image_link = p_soup.find('table', class_='infobox').find('img').get('srcset')
        image_link = image_link[image_link.rfind('//'):image_link.find(' 2x')]
        person = {
            'name': p_soup.find('th', class_='infobox-above').get_text().lower(),
            'p_link': p_link,
            'b_date': f.get_dig_date(p_soup.find('span', class_='bday').get_text(), 2),
            #'ef_date': table.find('span', class_='no-wikidata').find_next('a').find_next('a').get_text() + " " + table.find('span', class_='no-wikidata').find_next('a').find_next('a').find_next('a').get_text(),
            'image_link': 'https:' + image_link,
            'work': work
        }
        return person
    except:
        return 1


def parser(URL, cont_id=1, cont_id_work=37):
    log.debug(f"The script {__name__} starts working")
    html = f.get_html(URL)
    if html.status_code == 200:
        person = get_content(html, cont_id, cont_id_work)
        if person == 1:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
        content = []
        content.append({
            'first_name': person['name'].split()[0],
            'middle_name': person['name'].split()[1],
            'last_name': person['name'].split()[2],
            'link': person['p_link'],
            'bday': person['b_date']['day'],
            'bmonth': person['b_date']['month'],
            'byear': person['b_date']['year'],
            #'ef_date': get_dig_date(person['ef_date'].replace('года', '')),
            'image_link': person['image_link'],
            'position_id': person['work']
        })
        log.debug("The script stops working")
        return content
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]
