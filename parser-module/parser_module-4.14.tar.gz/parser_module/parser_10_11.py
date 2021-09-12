from parser_libraries import functions as f
from bs4 import BeautifulSoup
from parser_libraries import SQL
import os
import logging
import logging.handlers


logging.basicConfig(format=f'%(module)s.{__name__}: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



URL = 'https://www.mid.ru/activity/shots/personnel/extraordinary_ambassador#main-content'


def parser():
    log.debug(f"The script {__name__} starts working")
    info = SQL.get_con_info()
    html = f.get_selenium_html(URL, chromium=info['chromium_path'], driver=info['chromedriver_path'], params=info['use_chromium'])
    info = None
    soup = BeautifulSoup(html, 'html.parser')
    contents = soup.find('section', class_='block')
    contents = contents.find_all('tr')
    contents = contents[1:]
    people = []
    for content in contents:
        name = content.get_text().lower().replace('\n', ' ')
        while name.find('  ') != -1:
            name = name.replace('  ', ' ')
        work = name.find('ПОСТОЯННЫЙ ПРЕДСТАВИТЕЛЬ РОССИЙСКОЙ ФЕДЕРАЦИИ'.lower())
        if work == -1:
            work = 10
        else:
            work = 11
        try:
            date = name[name.find('.')-2:name.find('.')+8].replace('.', ' ')
            date = f.get_dig_date(date)
        except:
            date = f.get_dig_date('01 01 1901')
        name = name[1:name.find('.')-2]
        name = f.get_name(name)
        people.append({
            'image_link': '-',
            'first_name': name[1],
            'middle_name': name[2],
            'last_name': name[0],
            'link': URL,
            'bday': date['day'],
            'bmonth': date['month'],
            'byear': date['year'],
            'position_id': work
        })
    log.debug("The script stops working")
    return people

if __name__ == "__main__":
    SQL.mySQL_save(parser())