from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd


import sys
sys.path.append('..')

def import_packages():
    """
    This is where I can type in all the stuff that I can import with the project.

    TD have this integrated probably so text like above does not apear. 
    """
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


def save_data(name, input_list):
    df = pd.DataFrame(input_list)
    df.to_csv('{name}.csv', index = False, sep= ';')

def create_dict(*args):
    """
    Creates a dictionary with argument names as key names and values as values.

    input valued variables. 
    output dictionary
    """
    return dict({i:eval(i) for i in args})

def seperate_month_and_year(month_and_year):
    """
    month_and_year is normally found as a size 2 tuple. This seperates it into components.

    input length 2 tuple. output length two list.

    TD have this raise a value error if something other than the usual input is inserted. 
    """
    year, month = month_and_year
    dummy_list = [year, month]
    return dummy_list