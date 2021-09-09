import sys
sys.path.append('..')
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from test_common_functions import *




class Non_duplicate_lists():
    """
    This class is for lists that we wouldn't to have duplicates unless very specifically allowed. 

    TD (generally). thoroughly make sure weather some of these lists would be better off as dictionaries as they 
    """
    def __init__(self, input_list = []):
        self.input_list = input_list


    def reset_list(self):
        """
        Empties the list

        output: list
        """
        self.input_list = []
    
    @staticmethod
    def add_if_no_duplication(input_list, new_entry):
        """
        This function adds a new entry to the list only if it is not existing inside already. 


        input: List, List_entry (any acceptable list variable)
        output: List
        """
        item_found = False
        for items in input_list:
            if items == new_entry:
                item_found = True
        if item_found == False:
            input_list.append(new_entry)     
        return input_list   

    def alphabetise(self):
        """
        Orders the list. this means alphabetised list for strings.  

        input, output: list of strings  (optional)

        TD: incorpate this into searching algorithms. 
        """
        self.input_list.sort
    
    def return_list(self):
        return self.input_list


"""
Test functions
"""
def test_add_if_no_duplicant():
    test_list = []
    expected_value = [1, 2]
    non_duplicate_list = Non_duplicate_lists()
    non_duplicate_list.add_if_no_duplication(test_list, new_entry = 1)
    non_duplicate_list.add_if_no_duplication(test_list, new_entry = 1)
    non_duplicate_list.add_if_no_duplication(test_list, new_entry = 2)
    print(expected_value == test_list)
    
#test_add_if_no_duplicant()

#TD make it so that the code works without the above variable(s) and function(s)






class Rigid_Parameters_Selection():
    """
    These variables should never be changed. 

    For example there will very likely never be a different list of months.

    TD Implement this properly so it is private
    
    """
    def return_list_of_month_names():
        """
        return a list of all the months

        output: list
        """
        return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    def return_month_number_match():
        """
        returns a dictionary matching the month with the position it has in a year.

        outputs: Dictionary with string key and integer output. 
        """
        return [{'Month': 'January', 'Number': '1'},
                      {'Month': 'February', 'Number': '2'}, 
                      {'Month': 'March', 'Number': '3'}, 
                      {'Month': 'April', 'Number': '4'}, 
                      {'Month': 'May', 'Number': '5'}, 
                      {'Month': 'June', 'Number': '6'},
                      {'Month': 'July', 'Number': '7'},
                      {'Month': 'August', 'Number': '8'},
                      {'Month': 'September', 'Number': '9'},
                      {'Month': 'October', 'Number': '10'},
                      {'Month': 'November', 'Number': '11'},
                      {'Month': 'December', 'Number': '12'},] 
rigid_parameters = Rigid_Parameters_Selection
#TD This ideally should not be needed here but code wouldn't work without it. Find out how to improve this.         


"""
Testing
"""

def test_rigid_parameters():
    """
    As this is a simple class. This should be enough. 
    """
    expected_value = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    rigid_tester = Rigid_Parameters_Selection
    output = rigid_tester.return_list_of_month_names() #Expected output is the list of the month names e.g ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    print(expected_value == output)

#test_rigid_parameters




class Parameters_selection():
    """
    These parameters are likely to be changed. They can all be found here without digging through the code.

    The function names usually contatin the name of the variable being used.  

    outputs vary. 
    """
    def return_amount_of_ranks():
        return 16
    def return_date_text_identifier():
        return 'mw-changeslist-date'
    def return_end_date():
        return ['16:08, 6 August 2020']
    def return_exchange_URL():
        return 'https://en.wikipedia.org/w/index.php?title=List_of_stock_exchanges&action=history'
    def return_format_change_dates():
        return ['02:17, 22 April 2021']
    def return_history_name():
        return 'historySearch'
    def return_skipped_dates():
        return ['07:40, 24 January 2021']
    def return_weather_URL():
        return 'https://www.wunderground.com/history' 
    def return_URL_sleeping_list():
        return [4, 4, 1, 2, 2]
    def return_weather_sleeping_list():
        return [4, 4]
    def return_diff_name_dict():
        return {'Hong Kong' : 'Kowloon', 'Mexico City': 'IMEXICOC52'}
    def return_correct_link_length():
        return 36

    def return_desired_scraped_months():
        return [('2021', 'September'),('2021', 'August'),('2021', 'July'),
            ('2021', 'June'),('2021', 'May'),('2021', 'April'),
            ('2021', 'March'),('2021', 'February'),('2021', 'January'),
            ('2020', 'December'), ('2020', 'November'),('2020', 'October'),
            ('2020', 'September'),('2020', 'August') ]

#TD This ideally should not be needed here but code wouldn't work without it. Find out how to improve this.  
"""
Testing for class
"""
def test_return_desired_scraped_months():
    test_parameters = Parameters_selection()
    output = test_parameters.return_desired_scraped_months
    expected_value = [(2021, 'September'),(2021, 'August'),(2021, 'July'),
            (2021, 'June'),(2021, 'May'),(2021, 'April'),
            (2021, 'March'),(2021, 'February'),(2021, 'January'),
            (2020, 'December'), (2020, 'November'),(2020, 'October'),
            (2020, 'September'),(2020, 'August') ]
    print(expected_value == output)

#test_return_desired_scraped_months
#print(our_parameters.return_exchange_URL())   


class Saved_values():
    
    def __init__():
        pass
    
    @staticmethod
    def initalise_values():
        global saved_url_scrape, saved_wikipedia_scrape, saved_weather_scrape
        saved_url_scrape = []
        saved_wikipedia_scrape = []
        saved_weather_scrape = []
    
    @staticmethod
    def reset_variable(input):
        input 









class Matching_Dictionary():
    """
    Little used class for future incorportion.  This is a list of dictionaries where 'the left values' the keys are strongly linked to 'the right values' the values. 

    TD incorporate this into code more. A dictionary of dicitonaries woudld be way faster.  

    TD Comprehensive testing regarding other inputted lists.
    """
    def __init__(self, left_key, right_key, input_list):
        """
        The different variables used here .

        The input_list would be structured like the following:[{'Month': 'January', 'Number': '1'},
                      {'Month': 'February', 'Number': '2'}, 
                      {'Month': 'March', 'Number': '3'}, 
                      {'Month': 'April', 'Number': '4'}, 
                      {'Month': 'May', 'Number': '5'}, 
                      {'Month': 'June', 'Number': '6'},
                      {'Month': 'July', 'Number': '7'},
                      {'Month': 'August', 'Number': '8'},
                      {'Month': 'September', 'Number': '9'},
                      {'Month': 'October', 'Number': '10'},
                      {'Month': 'November', 'Number': '11'},
                      {'Month': 'December', 'Number': '12'},] 
        I.E a list containg dictionaries with two keys each. 


        TD it looks like the left key and the right key can possibly be derived somehow. 
        """
        self.left_key = left_key
        self.right_key = right_key
        self.input_list = input_list

    def change_list(self, input_list):
        """
        If you want the input list to change 
        """
        self.input_list = input_list


    def add_key():
        """
        TD
        """
        pass

    @classmethod
    def __iter__(self):
        return self

    def get_rightvalue_from_leftvalue(self, left_value):
        """
        This function gets us the matching value from the left value for any key which appears in any of the dictonaries. 

        In the only current implentation of this function, the code searches the dictonaries for one which contain the month we are looking for. 
        It then returns its correpsonging value. 

        TD add failure result. 

        """
        
        for dictionaries in self.input_list:
            if dictionaries[self.left_key] == left_value:
                return dictionaries[self.right_key]
        

    @classmethod
    def alphatbetise_by_left_key(cls):
        pass

    def return_inputs(self):
        """
        Returns the inputs. Incase place of inputs is hard to find. 
        """
        return [self.left_key, self.right_key, self.input_list]

"""
Testing
"""
def test_matching_dictionary():
    matching_test = Matching_Dictionary(left_key = 'Month', right_key = 'Number', input_list = rigid_parameters.return_month_number_match())   #The month number matcher is the dicitonary that appears in the class description.
    test_list = []
    test_list.append(matching_test.return_inputs())  #This should return the inputs we just put in. 
    test_list.append(matching_test.get_rightvalue_from_leftvalue(left_value = 'May')) #Expected results for these four: 5, 3, 6, 7
    test_list.append(matching_test.get_rightvalue_from_leftvalue(left_value = 'March'))
    test_list.append(matching_test.get_rightvalue_from_leftvalue(left_value = 'June'))
    test_list.append(matching_test.get_rightvalue_from_leftvalue(left_value = 'July'))
    expected_value = [['Month', 'Number', [{'Month': 'January', 'Number': '1'}, {'Month': 'February', 'Number': '2'}, 
        {'Month': 'March', 'Number': '3'}, {'Month': 'April', 'Number': '4'}, 
        {'Month': 'May', 'Number': '5'}, {'Month': 'June', 'Number': '6'}, 
        {'Month': 'July', 'Number': '7'}, {'Month': 'August', 'Number': '8'}, 
        {'Month': 'September', 'Number': '9'}, {'Month': 'October', 'Number': '10'}, 
        {'Month': 'November', 'Number': '11'}, {'Month': 'December', 'Number': '12'}]], '5', '3', '6', '7']
    print(test_list == expected_value)
#test_matching_dictionary()

class Month_And_Year():
    """
    A combination of month and year.

    The month is as a word (i.e 'May'). The year is as a four digit string (i.e 2010)
    """
    def __init__(self, month, year):
        """
        month and year are defined here
        """
        self.month = month
        self.year = year
    def get_month_number(self):
        """
        This functions gets the position of a month in a year based on its name

        input: string
        output: integer (1 to 12)
        """
        month_number_matcher = Matching_Dictionary(left_key = 'Month', right_key = 'Number', input_list = rigid_parameters.return_month_number_match())
        return month_number_matcher.get_rightvalue_from_leftvalue( left_value = self.month)

    def get_amount_of_days(self):
        """
        This function finds the amount of days in a month given the name of the month.

        output: integer (28 to 31)
        
        """
        if self.month in ('July', 'May', 'March', 'January', 'December', 'October','August'):  
            amount_of_days = 31
        elif self.month in ('June', 'April', 'November', 'September'): 
            amount_of_days = 30
        elif int(self.year) %4 == 0: #A test for whether the year is a leap year or not. This is sufficient logic in the span of dates we are looking at. 
            amount_of_days = 29
        else:
            amount_of_days = 28
        return amount_of_days
    def return_month(self):
        """
        Seems superflous but can maybe come in handy
        """
        return self.month


    def return_year(self):
        """
        Seems superflous but can maybe come in handy. Good for testing initialisation 
        """
        return self.year


    def return_month_and_year_tuple(self):
        """
        This method joins the month and year together.
        """
        return (self.year, self.month)

"""
Testing
"""

def test_month_and_year():
    march_2020 = Month_And_Year(month = 'March', year = 2020)
    feb_2021 = Month_And_Year(month = 'February', year = 2021)
    feb_2020 = Month_And_Year(month = 'February', year = 2020)

    
    test_month_number_return_list = []
    test_amount_of_days_rl = []
    test_tuple_rl = []

    expected_number_return_list = ['3', '2']
    expected_tuple = ['March', 2020, (2020, 'March')]
    expected_amount_of_days = ['3', '2', 28, 29, 31]
    expected_month_numbers = ['3', '2']

    test_amount_of_days_rl.append(march_2020.get_month_number()) #Expected values: 3 and 2.
    test_amount_of_days_rl.append(feb_2020.get_month_number())
    print(test_amount_of_days_rl == expected_number_return_list)
    
    test_tuple_rl.append(march_2020.return_month())
    test_tuple_rl.append(march_2020.return_year()) #Expected values for these three are March, 2020 and (2020, March) respectively
    test_tuple_rl.append(march_2020.return_month_and_year_tuple())
    print(test_tuple_rl == expected_tuple)

    test_amount_of_days_rl.append(feb_2021.get_amount_of_days())
    test_amount_of_days_rl.append(feb_2020.get_amount_of_days())
    test_amount_of_days_rl.append(march_2020.get_amount_of_days())   #This is where a test for these days of the month. These all give the correct amount of days
    print(test_amount_of_days_rl == expected_amount_of_days)

    test_month_number_return_list.append(march_2020.get_month_number())
    test_month_number_return_list.append(feb_2021.get_month_number())
    print(test_month_number_return_list == expected_month_numbers)

#test_month_and_year()




class Scraping_Space():
    """
    General scraping mechanism. 
    
    This includes functions common to different scrapers. 
    """
    def __init__(self):
        pass


    @staticmethod
    def get_all_children(current_driver, xpath):
        """
        This is for tables and such. It creates a list of the webelements from a table (or over encompassing web object).

        This usability of this function relies heavily. On how the output is used. 

        TD. add categories to the different web elements being outputted so the outputs are less likely to break later. 

        input: xpath
        output: list of web elements.
        """
        dummy_var = current_driver.find_element_by_xpath(xpath)
        dummy_list = dummy_var.find_elements_by_xpath("*")
        return dummy_list


    @staticmethod
    def outputting_dict(list_of_keys, list_of_data):
        """
        Outputs a dictionary created from two lists resembelming the keys and values specifically. 

        TD. Incorporate this into code. 
        """
        output_dict = {}
        looper = 0 
        for names in list_of_keys:
            output_dict[names] = list_of_data[looper]
            looper += 1
        return output_dict
        
    @staticmethod
    def go_to_link(current_driver, link):
        """
        Make the driver go to the inputted link. 
        """
        current_driver.get(link)
    
    @staticmethod
    def close_driver(driver):
        """
        closes the driver.

        TD: Check this is unused then delete, redundant.
        """
        driver.close
"""
Testing
"""


#test_scraping_space = Test_Scraping_Space()
#test_driver = test_start_driver()  #These first two lines test the functionality in opening the driver. 
#test_scraping_space.go_to_link(test_driver, 'https://en.wikipedia.org/w/index.php?title=List_of_stock_exchanges&oldid=1040911711') #These two tests succesfully open the driver and go to the wikipedia link. 

# The following test the get all children method. This should return a list of web elements. The expected result is a large amount of '<class 'selenium.webdriver.remote.webelement.WebElement'> being printed
#test_list = test_scraping_space.get_all_children(current_driver = test_driver, xpath = '//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[1]')
#for webelement in test_list:
 #   print(type(webelement))
#for link in test_list:
#Found_date = link.find_element_by_class_name('mw-changeslist-date')
# Found_date_text = Found_date.text
# # print(Found_date.text)

#test_list_of_keys = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth']
#test_list_of_data = [0, [1, 2], 'hello', 'hello, again', [12, 23, 34], 5]

#An independent test for the this method. Expected output = {'First': 0, 'Second': [1, 2], 'Third': 'hello', 'Fourth': 'hello, again', 'Fifth': [12, 23, 34], 'Sixth': 5}
#print(test_scraping_space.outputting_dict(test_list_of_keys, test_list_of_data))

#This section tests the close driver function. If it works then the go to link method won't do anything
#test_scraping_space.close_driver(test_driver)
#test_scraping_space.go_to_link(test_driver, 'https://en.wikipedia.org/w/index.php?title=List_of_stock_exchanges&oldid=1040911711'
