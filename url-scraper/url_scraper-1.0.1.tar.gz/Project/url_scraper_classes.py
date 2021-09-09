import sys
from weather_scraper_classes import Weather_Xpath_Selection
sys.path.append('..')
from main_classes import Parameters_selection, Scraping_Space
from weather_scraper_classes import Weather_Xpath_Selection
from common_functions import *
import time 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

global saved_url_scrape

our_parameters = Parameters_selection
weather_xpaths = Weather_Xpath_Selection


class Location_Url_Scrape(Scraping_Space):
    """
    Methods can be found here to do with the scraping of the URLS.

    This scraping finds the four letter code associated with the location in each URL. There are also methods for outputting this dictionary. 
    """
    def __init__(self, sleeping_amounts):
        self.sleeping_amounts = sleeping_amounts
    
    @staticmethod
    def reset_location_urls(location_urls = []):
        """
        Resets the usuual output list, the list of urls, to the default value.

        output = []
        """
        location_urls = []
        return location_urls

    def location_scrape(self, driver, location, location_urls = []):
        """
        For a single location, it would search the location of the weather homepage, then get the url from the search result. 

        Inputs: The driver we are using, the location we are looking for and the current list of urls (location_urls) which we want outputted.

        Output: Updated list of location urls. 
        """
        driver.get(our_parameters.return_weather_URL())
        time.sleep(self.sleeping_amounts[0])
        search_bar = driver.find_element_by_name(our_parameters.return_history_name())   #This is the search bar
        search_bar.click()

        location = self.location_name_matcher(location)

        search_bar.send_keys(location)  #This types the location in. 
        time.sleep(self.sleeping_amounts[1])
        search_bar.send_keys(Keys.RETURN) #Pressing enter after a delay will send you to a page regarding that location. 
        view_button = driver.find_element_by_xpath(weather_xpaths.get_search_button())
        view_button.click()
        view_button.click()  #This activate button needs to be clicked twice
        time.sleep(self.sleeping_amounts[2])  
        current_url = driver.current_url
        time.sleep(self.sleeping_amounts[3])
        location_urls.append(current_url) 

        time.sleep(self.sleeping_amounts[4])
        driver.get(our_parameters.return_weather_URL())  #Return to searchpage            



        current_url = driver.current_url
        save_data('url_data', location_urls) #The data is being saved here. 
        return location_urls
        


    
    def complete_url_scrape(self, driver, list_of_locations, location_urls):
        """
        For a list of locations, this will scrape through and find a corresponding list of urls. 

        This method mainly is doing the location scraper several times. 

        input: list of locations.
        output: corresponding list of urls
        """
        global saved_url_scrape
        for location in list_of_locations:
            saved_url_scrape = self.location_scrape(driver,  location, location_urls)

        driver.quit()
        saved_url_scrape = location_urls
        return location_urls
    
    @staticmethod
    def location_name_matcher(location):
        """
        This function searches a dictionary to see if the name needs to be changed while searching.

        Most names of locations give their correct destination as their first result. If the location is in this dictionary, it would need to be changed. 

        You need to input the name of a possible location (str)

        As an output, it will changed the name of the location if it is found in the dictionary. If not, it will output the unchanged name.

        """
        diff_name_dict = our_parameters.return_diff_name_dict()
        if location in diff_name_dict:
            location = diff_name_dict[location]
        return location