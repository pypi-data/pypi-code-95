from test_main_classes import Parameters_selection, Rigid_Parameters_Selection
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from test_main_classes import Scraping_Space
import time
import pandas as pd
from Project.common_functions import *
import sys
sys.path.append('..')
our_parameters = Parameters_selection
rigid_parameters = Rigid_Parameters_Selection

class Wikipedia_Xpath_selection():
    """
    This is where the user can change certain xpaths easily without having to find all the usages in the code. 

    These cover the xpaths from wikipeeida. The function title normally contains the name of the usual variable name making it easy to type in and refer to. 
    These all return strings 

    TD: Make this a subclass of some sort of all encompassing variable selector. 

    """
    def get_five_hundred_button():
        """
        This is the button that changes the amount of edit histories displayed from 50 to 500, a better page to scrape from
        """
        return '/html/body/div[3]/div[3]/div[4]/a[7]'
        
    def get_full_edit_list():
        return '//*[@id="pagehistory"]'
    def get_table_header():
        return '//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[1]'
    def get_page_table_unchanged_format():
        """
        At some point the format of the list changes. Different xpaths are needed depending on this. 
        """
        return '/html/body/div[3]/div[3]/div[5]/div[1]/table[2]/tbody'
    def get_page_table_changed_format():
        """
        At some point the format of the list changes. Different xpaths are needed depending on this. 
        """
        return '/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody'
wikipedia_xpaths = Wikipedia_Xpath_selection

def test_wikipedia_xpath_selection():
    expected_value = '/html/body/div[3]/div[3]/div[4]/a[7]'
    output = wikipedia_xpaths.get_five_hundred_button()
    return expected_value == output

#print(test_wikipedia_xpath_selection())





class Stock_Scraping_Space(Scraping_Space):
    """
    This is the scraping mechnism for the stock exchange, the wikipedia pages, specifically. 
    """
    def __init__(self, sleeping_amounts = []):
        """
        We are inheriting from the Scraping Space. 
        """
        super().__init__()
        self.sleeping_amounts = sleeping_amounts

    @staticmethod
    def go_to_home(exchange_URL, driver):
        """
        This static method takes us to our homepage.
        """
        driver.get(exchange_URL)
        fivehundred_link = driver.find_element_by_xpath(wikipedia_xpaths.get_five_hundred_button())
        fivehundred_link.click()


   # def check_format_change(change_of_format, second_driver):
    #        if  change_of_format == False:
     #           page_table = second_driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[5]/div[1]/table[2]/tbody')
      #      else:
       #         page_table = second_driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody')
    @staticmethod
    def check_format_change(written_date_text):
        if written_date_text in our_parameters.return_format_change_dates():
            return True
        else:
            return False

    @staticmethod
    def check_end_date(written_date_text):
        if written_date_text in our_parameters.return_end_date():
            return True
        else:
            return False
    



    def return_edit_list(self, driver):
        """
        This method gives us the list of edits to go through from the home page. This would work if and only if we are at the homepage. 
        """
        try:
            return self.get_all_children(driver, wikipedia_xpaths.get_full_edit_list())
        except:
            pass
    
    @staticmethod
    def return_page_table(second_driver, change_of_format):
        if change_of_format == False:
            return second_driver.find_element_by_xpath(wikipedia_xpaths.get_page_table_unchanged_format())
        else:
            return second_driver.find_element_by_xpath(wikipedia_xpaths.get_page_table_changed_format())

    def complete_stock_scrape(self):
        """
        This is the complete process of scraping for data from wikipedia. 
        
        """
        completed_months_and_years = []
        complete_list = []
        list_of_locations = []
        change_of_format = False
        driver = start_driver()
        self.go_to_home(our_parameters.return_exchange_URL(), driver)
        edit_list = self.return_edit_list(driver)
        self.return_edit_list(edit_list, driver, complete_list, list_of_locations, completed_months_and_years)


    @staticmethod
    def get_month_and_year_from_text(written_date_text = '12:07, 27 August 2021'):
        """
        This returns the month and year given a string containing both.

        input: String

        Output: tuple of year and month
        """
        current_year =  written_date_text[-4:]
        for month in rigid_parameters.return_list_of_month_names():
            if month in written_date_text:
                current_month = month
        return (current_year, current_month)
    
    @staticmethod
    def scrape_through_rows_of_table(list_of_rows, this_months_dictionary):
        """
        We go to a table and can scrapped through it to get imformation. There are no nested scraping methods inside this method. 
        """
        
        for row in list_of_rows:
            list_of_row_elements = row.find_elements_by_xpath("*")
            for row_elements in list_of_row_elements:
                k = 1   #This k indicates which column we are concerned with

                if len(list_of_row_elements) == 16:
                    if k == 1:  #This column corresponds to the rank of the exchange. 
                        this_months_dictionary['months_rank_list'].append(row_elements.text)

                    if k ==3: #This column corresponds to the name of the exchange.
                        this_months_dictionary['months_exchange_list'].append(row_elements.text)

                    if k == 6:
                        split_locations = row_elements.text.split('\n')
                        this_months_dictionary['months_location_list'].append(split_locations)

                    if k == 7:  #This column corresponds to the market's market cap. 
                        this_months_dictionary['months_market_cap_list'].append(row_elements.text)

                    if k ==8: # This column corresponds to the market's trade volume
                        this_months_dictionary['months_trade_volume_list'].append(row_elements.text)
            



                k += 1 #  Move to the next column 
            return(this_months_dictionary)

    def scrape_current_month(self,  change_of_format, written_date_link, this_months_dictionary = {'months_rank_list' : [], 'months_exchange_list' : [], 'months_location_list' : [], 'months_market_cap_list' : [], 'months_trade_volume_list' : [], 'current_column' : [], 'table_header_children' : []}):
        """
        A month has been selected. We can scrapped through the wikipedia page for this month. 
        """
        global months_rank_list, months_exchange_list, months_location_list, months_market_cap_list, months_trade_volume_list, current_column, table_header_children
        months_exchange_list = []
        months_location_list = []
        months_market_cap_list = []
        months_trade_volume_list = []
        #this_months_dictionary = create_dict("months_rank_list", "months_exchange_list", "months_location_list", "months_market_cap_list", "months_trade_volume_list")

        current_column = 0
                 
        second_driver = webdriver.Chrome('chromedriver.exe') # It makes it easier if we use a second driver to open links to a new window. 
        second_driver.get(written_date_link)
        

        table_header_children = self.get_all_children(second_driver, wikipedia_xpaths.get_table_header())
        page_table = self.return_page_table(second_driver, change_of_format)
        list_of_rows = page_table.find_elements_by_xpath("*")
        print(list_of_rows)
        this_months_dictionary = self.scrape_through_rows_of_table(list_of_rows, this_months_dictionary)


        second_driver.quit()
        return this_months_dictionary


    #@staticmethod
    #def rename_keys(this_months_dictionary):
        ##"""
        #It is convient to change the keys as they are less specific going forward.
        #"""
        ##this_months_dictionary['Rank'] = this_months_dictionary.pop('months_rank_list')
        #this_months_dictionary['Name of exchange'] = this_months_dictionary.pop('months_exchange_list')
        #this_months_dictionary['Locations'] = this_months_dictionary.pop('months_location_list')
        #this_months_dictionary['Market Cap'] = this_months_dictionary.pop('months_market_cap_list')
        #this_months_dictionary['Trade Voume'] = this_months_dictionary.pop('months_trade_volume_list')

    @staticmethod
    def add_locations_to_distinct_list(list_of_locations, this_months_dictionary):
        for location in this_months_dictionary['months_location_list']:
            if location not in list_of_locations:
                list_of_locations.append(location)

    @staticmethod
    def create_month_location_match(month_and_year, month_location_list):
        """
        This creats a dictionary that matches the months with the locations. 
        """
        dictonary = {}
        dictonary[month_and_year] = month_location_list
        return dictonary

    @staticmethod
    def return_last_scraped_month_data(complete_list, last_scraped_month):
        """
        This returns the data from the last scrapped month so we can copy it to the skipped month.
        """
        for month in complete_list:
            if month[0] == last_scraped_month:
                return month[1]

    def scrape_through_edit_list(self, edit_list, complete_list, list_of_locations, completed_months_and_years):
        """
        We are scraping through the edit list to get links and data from it. 
        """
        month_and_year = []
        
        last_scraped_month = ''
        for link in edit_list:
            reset_variable(month_and_year)
            written_date = link.find_element_by_class_name(our_parameters.return_date_text_identifier()) # The text here gives us the date
            written_date_link = written_date.get_attribute('href')
            written_date_text = written_date.text


            if self.skip_date(written_date_text) == True:
                continue
            
            month_and_year = self.get_month_and_year_from_text(written_date_text)
            
            
            if self.check_shall_month_be_scraped(month_and_year, completed_months_and_years) == True:
                this_months_dictionary = self.scrape_current_month(self.check_format_change(written_date_text), written_date_link)
                complete_list.append([month_and_year, this_months_dictionary])     
                print(complete_list)                   
                completed_months_and_years.append(month_and_year)
                self.add_locations_to_distinct_list(list_of_locations, this_months_dictionary)
                month_location_match = self.create_month_location_match(month_and_year, this_months_dictionary['months_location_list'])

                self.copy_data_to_skipped_month(complete_list, this_months_dictionary, completed_months_and_years, list_of_locations, month_and_year)

                last_scraped_month = month_and_year


            if self.check_end_date(written_date_text) == True:
                self.copy_data_to_skipped_month(complete_list,completed_months_and_years, list_of_locations, month_and_year, this_months_dictionary = self.return_last_scraped_month_data(complete_list, last_scraped_month))
                break
            
        return (complete_list, list_of_locations, month_location_match)

    
    def copy_data_to_skipped_month(self, complete_list, completed_months_and_years, list_of_locations, month_and_year, this_months_dictionary):           
        """
        If a desired month is skipped. The data fromt the next desired month is used as a subsitiute.

        A month can be skipped if there was no edit data for that month

        output: a list containgin data for that month. 
        """
        for skipped_month in our_parameters.return_desired_scraped_months():
            try:
                #This is succesfu; only if month and year is desired
                if our_parameters.return_desired_scraped_months().index(skipped_month) < our_parameters.return_desired_scraped_months().index(month_and_year) and skipped_month not in completed_months_and_years:
                    complete_list.append([skipped_month, this_months_dictionary])                        
                    completed_months_and_years.append(skipped_month)
                    self.add_locations_to_distinct_list(list_of_locations, this_months_dictionary)
                    self.create_month_location_match(month_and_year = skipped_month, location_list = this_months_dictionary['months_location_list'])       
            except:
                pass

    @staticmethod
    def check_if_month_is_desired(month_and_year):
        """
        This checks the desired month list to see if the inout is inside it.

        input: tuple: year and month

        output: True/False
        """
        if month_and_year in our_parameters.return_desired_scraped_months():
            
            return True

        else:
            return False
            


    def check_shall_month_be_scraped(self, month_and_year, completed_months_and_years):
        """

        """
        if month_and_year in completed_months_and_years:
            return False
        else:
            return self.check_if_month_is_desired(month_and_year)


    @staticmethod
    def find_next_desired_month(month_and_year):
        """
        We have a list of desired months. This method gives us the next month in that list given an inputed month in the list.

        input: tuple: year and month

        output: tuple: year and month
        """
        try:
            index = our_parameters.return_desired_scraped_months().index(month_and_year)
            return our_parameters.return_desired_scraped_months()[index + 1]
        except:  #This happens when we have reached the endff of our desired range. 
            return our_parameters.return_desired_scraped_months()

                
    @staticmethod
    def skip_date(written_date_text):
        """
        When a date is entered. This method checks if the date needs to be skipped in the for loop.

        input: string (date)
        
        output: True or False.
        """
        if written_date_text in our_parameters.return_skipped_dates():
            return True
        else:
            return False

save_weather_scrape = []

#print(our_parameters.return_skipped_dates())

"""
Testing:
"""
class Test_Stock_Scrape():
    def __init__(self):
        self.tester = Stock_Scraping_Space()
    
    def test_skip_date(self):
        """
        Tests whether we get the right boolean variable for a skipped date and a unskipped date. 
        """
        test_list = []
        expected_value = [True, False]
        skipped_date = '07:40, 24 January 2021'
        not_skipped_date = '19:14, 6 July 2021'
        test_list.append(self.tester.skip_date(skipped_date))
        test_list.append(self.tester.skip_date(not_skipped_date))
        print(test_list == expected_value)
    
    def test_find_next_desired_month(self):
        expected_value = (2021, 'March')
        return expected_value == self.tester.find_next_desired_month((2020, 'August'))
    
    def test_return_edit_list(self):
        """
        A test to see if the correct edit list is returned. Manual inspection has identified this as the correct edit list. 
        """
        td = start_driver()
        scraper.go_to_home(our_parameters.return_exchange_URL(), driver = td)
        return self.tester.return_edit_list(td)
        
    def test_get_month_and_year_from_text(self):
        input = '12:07, 27 August 2021'
        expected_value = ('2021', 'August')
        return expected_value == self.tester.get_month_and_year_from_text('12:07, 27 August 2021')


    def test_scrape_through_edit_list(self):
        td = start_driver()
        scraper.go_to_home(our_parameters.return_exchange_URL(), driver = td)
        t_edit_list = self.test_return_edit_list()
        return self.tester.scrape_through_edit_list(t_edit_list, complete_list=[], list_of_locations=[], completed_months_and_years = []) 
    
    def test_shall_month_be_scraped(self):
        pass
scraper = Stock_Scraping_Space()




test_stock = Test_Stock_Scrape()

#print(test_stock.test_get_month_and_year_from_text())
print(test_stock.test_scrape_through_edit_list()[2])
print(test_stock.test_scrape_through_edit_list()[1])

#test_stock.test_skip_date()
#print(test_stock.test_find_next_desired_month())