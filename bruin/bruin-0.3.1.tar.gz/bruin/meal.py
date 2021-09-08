import requests
from bs4 import BeautifulSoup
from typing import Dict
from html import unescape
from termcolor import colored
from datetime import datetime
from unidecode import unidecode
from enum import Enum

MENU_URL = "http://menu.dining.ucla.edu/Menus"
HOUR_URL = "http://menu.dining.ucla.edu/Hours"

class Period(Enum):
    """
    Enum for different meal periods
    """
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"

    @classmethod
    def contains(cls, input: str) -> bool:
        """
        Check whether a string is one of the period.
        
        Parameters:
            input: the string we want to check
        
        Returns:
            a boolean indicating whether the input is a Period
        """
        try:
            cls(input)
        except:
            return False
        return True

def _get_html(url: str) -> str:
    """
    Return HTML raw text from a URL

    Parameters:
        url: the url to the website we want to fetch
    Returns:
        a raw text of the website
    Raise:
        exception when there is a network error.
    """
    request = requests.get(url)
    if request.status_code == 200:
        return request.content
    else:
        raise Exception("Network Error! Check your connection.")

def _format_output(html: str) -> Dict[str, Dict[str, list]]:
    """
    Extract information from the menu website and parse it
    into the dict for printing

    Parameters:
        html: the raw text of the website
    Return:
        dict
    """
    soup = BeautifulSoup(html, "lxml")
    res_dict = {}

    times = soup.find_all('h2')
    menu_blocks = soup.find_all('div', {'class': "menu-block whole-col"})
    meal_dict = dict(zip(times, menu_blocks))
    for time, menu_block in meal_dict.items():
        period = time.text
        res_dict[period] = {}
        restaurants = menu_block.find_all('h3')
        menu = menu_block.find_all("ul", {"class": "sect-list"})
        menu_dict = dict(zip(restaurants, menu))

        for key, value in menu_dict.items():
            name = key.text
            res_dict[period][name] = []
            dishes = value.find_all('a', {"class": "recipelink"})
            for link in dishes:
                res_dict[period][name].append(unescape(link.text))
    
    return res_dict

def _print_menu(menu_dict: Dict[str, Dict[str, list]]) -> None:
    """
    Print the menu dictionary
    """
    for key, value in menu_dict.items():
        print(colored(key+":\n", "blue", attrs=['bold']))
        for dining_hall, dishes in value.items():
            print(colored(dining_hall+":", "white", attrs=['bold']))
            for dish in dishes:
                print("\t"+dish)
            print("")

def print_menu_all() -> None:
    """
    Print Overview menu
    """
    _print_menu(_format_output(_get_html(MENU_URL)))

def print_menu_detail_all(type: Period) -> None:
    """
    Print detail menu for a specific period
    Parameter:
        type: a meal Period
    """
    _print_menu(_format_output(_get_html(MENU_URL+"/"+type)))

def _get_hour_info_all() -> Dict[str, Dict[str, str]]:
    """
    Fetch hour of operation info for each dining hall
    Return:
        a dictionary from dining hall to hour of operation
    """
    url = HOUR_URL + "/" + datetime.now().date().strftime("%Y-%m-%d")
    html = _get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    res_dict = {}

    table = soup.find('table', {'class': 'hours-table'})
    table_heads = table.find('thead').find('tr').find_all('th', {'class': 'hours-head'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    period = []
    for header in table_heads:
        content = unidecode(header.text).strip()
        if content != "":
            period.append(header.text)
    
    for row in rows:
        cols = row.find_all('td')
        dining_hall = cols[0].find('span').text
        ranges = []
        for i in range(1, len(cols)):
            if cols[i].find('span'):
                ranges.append(cols[i].find('span').text.strip(' \r\n'))
            else:
                ranges.append(cols[i].text.strip(' \r\n'))
        
        res_dict[dining_hall] = dict(zip(period, ranges))
    
    return res_dict

def print_hour_all() -> None:
    """
    Print hour of operation for every dining hall
    """
    hour_dict = _get_hour_info_all()
    date_string = datetime.now().date().strftime("%B %d, %Y")
    print(colored(date_string+"\n", 'cyan', attrs=['underline']))
    for key, value in hour_dict.items():
        print(colored(key+":", 'white', attrs=['bold']))
        for period, range in value.items():
            print('\t', period, ': ', range)
        print("")

def print_hour(dining_hall: str) -> None:
    """
    Print hour of operation for one dining hall
    Parameters:
        dining_hall: the name of dining hall
    """
    hour_dict = _get_hour_info_all()
    date_string = datetime.now().date().strftime("%B %d, %Y")
    if dining_hall in hour_dict:
        print(colored(date_string+"\n", 'cyan', attrs=['underline']))
        print(colored(dining_hall+":", 'white', attrs=['bold']))
        for period, range in hour_dict[dining_hall].items():
            print('\t', period, ': ', range)
        print("")
    elif dining_hall == 'all' or dining_hall == '':
        print_hour_all()
    else:
        print(dining_hall, "is not opening today :(")


    

