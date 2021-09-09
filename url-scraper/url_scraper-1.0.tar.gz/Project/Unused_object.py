from main_classes import Matching_Dictionary
    
class Column_Condition_Matcher(Matching_Dictionary):
    """
    Unused class which would have given values in a table a place in a dictonary with the column header as key name. 
    """
    def __init__(self, input_list):
        self.left_key = 'Coloumn number'
        self.right_key = 'Property'
        self.input_list = input_list
    def return_new_dict(self):
        output_dict = {}
        for dicts in self.input_list:
            pass
        return output_dict

class Leaf_Xpath_Match(Matching_Dictionary):
    """ 
    another unused class in which the children with no descendants in a webpage match with their xpath. 

    The hope for this was to make a DPS algorithm to search through all xpaths in a webpage. 
    """
    def __init__(self, input_list):
        self.left_key = 'Property'
        self.right_key = 'Xpath'
        self.input_list = input_list
    def create_new_dict_from_scrape(self, driver):
        scraped_data = {}
        for item in self.input_list:
            print(item[self.left_key])
            print(item[self.right_key])
            a =  driver.find_element_by_xpath({item[self.right_key]})
            scraped_data[{item[self.left_key]}] = a.text
            print(item[self.left_key])
            print(item[self.right_key])
        return scraped_data