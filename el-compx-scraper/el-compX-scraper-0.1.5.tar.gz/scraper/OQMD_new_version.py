from numpy import add
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from sqlalchemy import create_engine
import pandas as pd
import time
from scraper.generic_scraper import Scraper

class CompoundScraper(Scraper):
    '''
    This class is used to represent a compound scraper.

    Features
    --------

    (1) Name 
    (2) Space Group
    (3) Volume
    (4) Band Gap


    Parameters
    ----------
    n       : int
              Defines the number of pages to extract data from
    
    root    : str
              Defines the URL to extract data from
    
    list    : list
              This initiates an empty list to append all necessary links
    
    features: dict
              A dictionary that defines the output for extracted target features

    Attributes
    ----------
    (1) n
    (2) root
    (3) list
    (4) features

    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def get_to_URL(self) -> None:
        
        '''
        This function opens the target URL prior to extraction.
        It depends on the parameter 'root'.

        '''

        self.driver.get(self.root)
        search_button = self.driver.find_element_by_xpath('//*[@id="submit-id-search"]')
        search_button.click()
        
    def load_data(self) -> None:
        '''
        This function loads all 
        the WebElements pending extraction.

        '''
        table_xpath = '//*[@id="ResultTable"]/tbody'
        table = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
        #table = self.driver.find_element_by_xpath('//*[@id="ResultTable"]/tbody')
        compound_list = table.find_elements_by_xpath('.//tr')[1:]
        for i in compound_list:
            self.list.append(i)

    def next_page_click(self):
        next_page_button = self.driver.find_element_by_xpath('//button[@class="next"]') 
        next_page_button.click()  


    def extract_data(self) -> None:
        '''
        This function extracts the target compound data 
        and stores it in a dictionary

        '''
        print('Extracting compounds data ...')
        
        print('Initialising ...')
        self.get_to_URL()

        for j in range(self.n):
            
            print(f"Extracting from Page_{j}")
            
            
            print('Loading data ...')
            # reload data due to stale element
            self.load_data()   

            for item in self.list:
                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)

                name = WebDriverWait(item, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, './/td[@width="60"]')))
                self.features['Name'].append(name.text)
            
                WebDriverWait(item, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, './/td[@width="50"]')))
                spacegroup = item.find_elements_by_xpath('.//td[@width="50"]')[3]
                band_gap = item.find_elements_by_xpath('.//td[@width="50"]')[5]
                self.features['Spacegroup'].append(spacegroup.text)
                self.features['Band_gap'].append(band_gap.text)
               
            
                
                WebDriverWait(item, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, './/td[@width="80"]')))
                volume = item.find_elements_by_xpath('.//td[@width="80"]')[1]
                self.features['Volume'].append(volume.text)



                # name = item.find_element_by_xpath('.//td[@width="60"]')
                # spacegroup = item.find_elements_by_xpath('.//td[@width="50"]')[3]
                # volume = item.find_elements_by_xpath('.//td[@width="80"]')[1]
                # band_gap = item.find_elements_by_xpath('.//td[@width="50"]')[5]
                # self.features['Name'].append(name.text)
                # self.features['Spacegroup'].append(spacegroup.text)
                # self.features['Volume'].append(volume.text)
                # self.features['Band_gap'].append(band_gap.text)
                # time.sleep(1)
            
            print(f"Going to page_{j+1}")
            self.next_page_click()
            time.sleep(10)
        print('Extraction Complete ... ')


        




