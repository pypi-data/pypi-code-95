import unittest
import sys
sys.path.append('..')
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def start_driver():
    """
    Starts a webdriver driver using the chromedriver in the folder. 

    returns driver
    """
    driver = webdriver.Chrome('chromedriver.exe') 
    return driver
#start_driver()
#This was clearly a success



def reset_variable(input):
    """
    Depending on the type of input. It will give some default values.
    
    can allow string integer list and boolean.
    returns same type of variable as input. 
    """
    
    
    if type(input) == str:
        input = ''
    if type(input) == int:
        input = 0
    if type(input) == list:
        input = []
    if type(input) == bool:
        """
        Be weary. This will always default to false (There are more false things than true things initally).
        """
        input = False
    return input

def test_reset_variable():
    """
    Checking if the main type of inputs are reset
    """
    test_list = []
    expectted_value = ['', 0, [], False]
    test_list.append(reset_variable('h')) #This is invisible 
    test_list.append(reset_variable(13))
    test_list.append(reset_variable([12, '']))
    test_list.append(reset_variable(True))
    print(expectted_value == test_list)

#test_reset_variable()





def create_dict(*args):
    """
    Creates a dictionary with argument names as key names and values as values.

    input valued variables. 
    output dictionary
    """
    return dict({i:eval(i) for i in args})


a = 15
b = 20
def test_create_dict():

    print({'a': 15, 'b': 20} == create_dict('a', 'b'))

#test_create_dict()


def seperate_month_and_year(month_and_year):
    """
    month_and_year is normally found as a size 2 tuple. This seperates it into components.

    input length 2 tuple. output length two list.

    TD have this raise a value error if something other than the usual input is inserted. 
    """
    year, month = month_and_year
    dummy_list = [year, month]
    return dummy_list

def test_seperate_month_and_year():
    expected_value = [2020, 'May']
    print(expected_value == seperate_month_and_year((2020, 'May')))
test_seperate_month_and_year()
#TD test a large scope of more actual months and years. 









#print(test_seperate_month_and_year((2020, 'May')))


