from collections import defaultdict


class Logger():
    def __init__(self, *args):
        self.logger_dict = defaultdict(list)
    
    """
    Return the logger 

    :return : the logger dict  
    """
    def get_logger(self):
        return self.logger_dict

    """
    Log a dictionary

    :param in_dict: a dictionary to be added to the logger
    """
    def log(self, in_dict):
        for key in in_dict.keys():
            self.logger_dict[key].append(in_dict[key])
        