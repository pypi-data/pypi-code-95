from parser_libraries import functions as f
from bs4 import BeautifulSoup
import os
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

URL = 'https://pravo.ru/arbitr_practice/courts/119/'


def parser():
    log.debug(f"The script {__name__} starts working")
    people = []
    html = f.get_html(URL)
    if html.status_code == 200:
        try:
            soup = BeautifulSoup(html.text, 'html.parser')
            items = soup.find('table', class_='no_stripes no_padding common_info')
            items = items.find_all('tr')
            for item in items:
                work = f.get_work(item.find('td', class_='muted').get_text().lower(), mode=24)
                name = f.get_name(item.find('a').get_text().lower())
                link = item.find('a').get('href')
                link_html = f.get_html(link)
                link_soup = BeautifulSoup(link_html.text, 'html.parser')
                link_soup = link_soup.find('div', class_='card')
                image_link = link_soup.find('img').get('src')
                text = link_soup.find('p').get_text()
                ind = text.find(' года')
                if ind == -1:
                    ind = text.find('г.')
                text = text[text.find(' ')+1:ind]
                date = f.get_dig_date(text)
                if date == -1:
                    text = text[text.find(":")+1:]
                    date = f.get_dig_date(text)
                people.append({
                    'image_link': image_link,
                    'first_name': name[1],
                    'middle_name': name[2],
                    'last_name': name[0],
                    'link': link,
                    'bday': date['day'],
                    'bmonth': date['month'],
                    'byear': date['year'],
                    'position_id': work
                })
            log.debug("The script stops working")
            return people
        except:
            return [{'code': 1, 'script': os.path.basename(__file__)}]
    else:
        return [{'code': 2, 'script': os.path.basename(__file__)}]

if __name__ == "__main__":
    print(parser())