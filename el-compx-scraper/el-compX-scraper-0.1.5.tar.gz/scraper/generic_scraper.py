#%%
from numpy import add
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait


class Scraper:

    '''
    This class represents a scraper.  

    Features
    --------

    (1) Name 
    (2) Space Group
    (3) Volume
    (4) Band Gap


    Parameters
    ---------
    n       : int
              Defines the number of pages to extract data from
    
    root    : str
              Defines the URL to extract data from
    
    list    : list
              This initiates an empty list to append all necessary links
    
    features: dict
              A dictionary that defines the output for extracted target features
              Example: features = {'Name':[], 'Spacegroup':[], 'Volume':[], 'Band_gap':[]}

    Attributes
    ----------
    (1) n
    (2) root
    (3) list
    (4) features
    
    '''
    
    def __init__(self, **kwargs):
        self.n = kwargs['n']
        self.root = kwargs['root']
        self.list = kwargs['list']
        self.features = kwargs['features']
        self.driver = webdriver.Chrome('chromedriver')
    

