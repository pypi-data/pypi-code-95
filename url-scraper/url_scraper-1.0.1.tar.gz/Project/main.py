from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from weather_scraper_classes import *
from url_scraper_classes import *
from wikipedia_scraper_classes import *
from main_classes import *
from common_functions import *


wikipedia_xpaths = Wikipedia_Xpath_selection
this_months_dictionary = {'months_rank_list' : [], 'months_exchange_list' : [], 'months_location_list' : [], 'months_market_cap_list' : [], 'months_trade_volume_list' : [], 'current_column' : [], 'table_header_children' : []}
exchange_URL = 'https://en.wikipedia.org/w/index.php?title=List_of_stock_exchanges&action=history'
weather_URL = 'https://www.wunderground.com/history'
certain_stock_exchange_url = 'https://en.wikipedia.org/w/index.php?title=List_of_stock_exchanges&oldid=1040911711'
x = our_parameters.return_URL_sleeping_list()

def scrape_wikipedia():
    """
    The main function that scrapes wikipedia
    """
    wikipedia_scraper = Stock_Scraping_Space()
    return wikipedia_scraper.complete_stock_scrape()

location_urls = []
locations_list = ['New York', 'Tokyo', 'Amsterdam', 'Berlin', 'Madrid']
def scrape_urls():
    """
    The main function that scrapes for the urls
    """
    url_scraper = Location_Url_Scrape(sleeping_amounts = our_parameters.return_URL_sleeping_list())
    driver = webdriver.Chrome('chromedriver.exe')
    return url_scraper.complete_url_scrape(driver = webdriver.Chrome('chromedriver.exe'), list_of_locations = locations_list, location_urls = [])



test_month_location_match = [{'Month': ('2020', 'November'), 'Locations' : ['New York' ,'London', 'Tokyo']},{'Month': ('2020', 'September'), 'Locations' : ['Tokyo' ,'London', 'Hong Kong']}, {'Month': ('2021', 'March'), 'Locations' : ['New York' ,'London', 'Oslo']}]
test_location_key_match = [{'Location Name': 'New York','key': 'KLGA'}, {'Location Name': 'London','key': 'EGLC'}, {'Location Name': 'Tokyo' ,'key': 'RJTT'}, {'Location Name': 'Hong Kong','key': 'VHHH'}, {'Location Name': 'Oslo','key': 'ENGM'}, ]
def scrape_weather():
    """
    The main function that scrapes the weather. 
    """
    weather_scraper = Weather_Scrape(Giant_dataset=[], location_key_match = test_location_key_match, month_location_match = test_month_location_match)
    return weather_scraper.complete_weather_scrape()

#scrape_wikipedia()
#scrape_urls()
scrape_weather()