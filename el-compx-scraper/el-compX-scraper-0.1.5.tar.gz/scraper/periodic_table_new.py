from numpy import add
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from scraper.data_structure import convert_to_DF 
import time
from scraper.generic_scraper import Scraper

class PeriodicTableScraper(Scraper):
    
    '''
    This class is used to represent a periodic table scraper.
    
    Features
    --------

    (1) Name 
    (2) Space Group
    (3) Volume
    (4) Band Gap


    Parameters
    ---------
    n       : int
              Defines the number of periodic table elements to extract data from 
    
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

    def extract_links(self) -> None :
        
        '''
        Extracts all urls for each periodic table element 
        and stores them in a list.

        '''
        print(f" --- Extracting elemental URLs ---")
        
        self.driver.get(self.root)
        element_list = self.driver.find_elements_by_xpath("//li[@class='p-md-bottom print-avoid-break-inside print-padding-top']")
        for item in element_list[0:self.n]:
                link = item.find_element_by_xpath('.//a').get_attribute('href')
                self.list.append(link)
        
        print(f"... Done")


    def extract_data(self, to_DF=False) -> None :
        
        '''
        Extracts information on specified features of 
        elements from the periodic table.

        Parameters
        ----------
        to_DF : bool
                Serves as a switch for converting the output extract data to a Data Frame.

        '''
        
        self.extract_links()
        for i in self.list:
            self.driver.get(i)
            time.sleep(3)
            atomic_no_xpath = '//div[@class="f-15"]'
            element_name_xpath = '//*[@id="Element-Name"]/div[2]/div[1]/p'
            electronegativity_xpath = '//*[@id="Electronegativity"]/div[2]/div[1]/p'
            boiling_point_xpath = '//*[@id="Boiling-Point"]/div[2]/div[1]/p'

            try:
                atomic_n = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, atomic_no_xpath)))
                element_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, element_name_xpath)))
                electronegativity = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, electronegativity_xpath)))
                boiling_point = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, boiling_point_xpath)))
                self.features['Element_Name'].append(element_name.text)
                self.features['Atomic_Number'].append(atomic_n.text)
                self.features['Boiling_Point'].append(boiling_point.text)
                self.features['Electronegativity'].append(electronegativity.text)
            except TimeoutException: 
                self.features['Electronegativity'].append('NA')
                self.features['Boiling_Point'].append('NA')
        print(f"--- Extracting elemental features ---")
        print(f" ... Done")
        
        if to_DF == True:
            print(f"converting to DF ...")
            convert_to_DF(self.features, 'elements_data', to_csv=True)
        else:
            pass











