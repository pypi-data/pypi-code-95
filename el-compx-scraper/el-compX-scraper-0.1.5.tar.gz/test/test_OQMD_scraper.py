import sys
import unittest
sys.path.append('/home/bilal/AiCourse/Webscraping_Project/scraper')
from OQMD_new_version import CompoundScraper

class CompoundScraperTestCase(unittest.TestCase):
    def test_get_to_URL(self):
        root = "http://oqmd.org/api/search#apisearchresult"
        features = {'Name':[], 'Spacegroup':[], 'Volume':[], 'Band_gap':[]}
        scraper = CompoundScraper(n=1, root=root, list=[], features=features)
        scraper.get_to_URL()
    
    def test_load_data(self):
        # testing the type of the load_data output
        # compare the lengths of expected output list and actual list 
        root = "http://oqmd.org/api/search#apisearchresult"
        features = {'Name':[], 'Spacegroup':[], 'Volume':[], 'Band_gap':[]}
        scraper = CompoundScraper(n=1, root=root, list=[], features=features)
        scraper.get_to_URL()
        scraper.load_data()
        expected_list_type = type([]) # FIX IT
        actual_list_type = type(scraper.list)
        expected_list_len = 50
        actual_list_len = len(scraper.list)
        self.assertEqual(expected_list_type, actual_list_type)
        self.assertEqual(expected_list_len, actual_list_len)
    
    def test_extract_data(self):
        # check if the number of elements are the same
        # check if the elements are different from each other , use self.assertItemsEqual
        root = "http://oqmd.org/api/search#apisearchresult"
        features = {'Name':[], 'Spacegroup':[], 'Volume':[], 'Band_gap':[]}
        scraper = CompoundScraper(n=1, root=root, list=[], features=features)
        scraper.extract_data()
        actual_output = scraper.features
        expected_output = {'Name': ['CsHoSiS4',  'Lu',  'Tm',  'Ne',  'La',  'Pr',  'Kr',  'V',  'Rb',  'Ta',  'V',  'Ne',  'Al',  'Ne',  'K',  'Rh',  'Er',  'Zr',  'Ho',  'Lu',  'Tb',  'Ne',  'P',  'Ru',  'Ir',  'Gd',  'Fe',  'Ni',  'Fe',  'Tc',  'Re',  'Pt',  'YbSe',  'SiP',  'SmZn',  'SiC',  'U',  'Zr',  'Os',  'ZnNi',  'TiAg',  'ZnNi',  'YbTe',  'TmAg',  'UTe',  'YAg',  'LiBi',  'TcB',  'LiTl',  'YbAg'], 'Spacegroup': ['P212121',  'R-3m',  'R-3m',  'Fm-3m',  'Im-3m',  'Im-3m',  'Fm-3m',  'Fm-3m',  'Im-3m',  'Fm-3m',  'Im-3m',  'Fm-3m',  'Fm-3m',  'Fm-3m',  'Im-3m',  'Fm-3m',  'Im-3m',  'Im-3m',  'Im-3m',  'Im-3m',  'Im-3m',  'Fm-3m',  'Pm-3m',  'Fm-3m',  'Fm-3m',  'Im-3m',  'Im-3m',  'Im-3m',  'Fm-3m',  'Fm-3m',  'Fm-3m',  'Fm-3m',  'Fm-3m',  'F-43m',  'Pm-3m',  'Fm-3m',  'Im-3m',  'Fm-3m',  'Fm-3m',  'P4/mmm',  'P4/mmm',  'Pm-3m',  'Fm-3m',  'Pm-3m',  'Pm-3m',  'Pm-3m',  'P4/mmm',  'Pm-3m',  'Pm-3m',  'Pm-3m'], 'Volume': ['760.627',  '86.351',  '88.611',  '21.720',  '37.786',  '35.887',  '42.831',  '13.515',  '89.599',  '18.788',  '13.169',  '22.212',  '16.483',  '11.262',  '71.876',  '13.986',  '30.711',  '22.806',  '31.050',  '29.429',  '32.046',  '10.226',  '14.572',  '13.798',  '14.465',  '32.540',  '11.174',  '10.860',  '10.198',  '14.563',  '14.946',  '15.540',  '51.335',  '37.415',  '47.871',  '16.624',  '20.053',  '23.185',  '14.340',  '23.962',  '33.974',  '24.026',  '63.967',  '45.446',  '52.510',  '47.706',  '47.134',  '20.315',  '41.175',  '48.189'], 'Band_gap': ['3.024',  '0',  '0',  '11.910',  '0',  '0',  '7.487',  '0',  '0',  '0',  '0',  '11.657',  '0',  '13.500',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '14.115',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '2.083',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '0',  '1.620',  '0',  '0',  '0',  '0',  '0',  '0',  '0']}
        self.assertCountEqual(actual_output, expected_output)

unittest.main(argv=[''], verbosity=2, exit=False)



