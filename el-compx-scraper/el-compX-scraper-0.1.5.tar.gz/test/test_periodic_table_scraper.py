import unittest
import sys
sys.path.append('/home/bilal/AiCourse/Webscraping_Project/scraper')
from periodic_table_new import PeriodicTableScraper

class PeriodicTableScraperTestCase(unittest.TestCase):
    def test_extract_links(self) -> None:
        root = "https://pubchem.ncbi.nlm.nih.gov/periodic-table/#view=list"
        features = {'Element_Name':[], 'Atomic_Number':[], 'Electronegativity':[], 'Boiling_Point':[]}
        element_scraper = PeriodicTableScraper(n=5, root=root, list=[], features=features)
        element_scraper.extract_links()
        expected_output = ['https://pubchem.ncbi.nlm.nih.gov/element/1', 'https://pubchem.ncbi.nlm.nih.gov/element/2', 'https://pubchem.ncbi.nlm.nih.gov/element/3', 'https://pubchem.ncbi.nlm.nih.gov/element/4', 'https://pubchem.ncbi.nlm.nih.gov/element/5']
        actual_output = element_scraper.list
        self.assertCountEqual(expected_output, actual_output)
    
    def test_extract_data(self) -> None:
        root = "https://pubchem.ncbi.nlm.nih.gov/periodic-table/#view=list"
        features = {'Element_Name':[], 'Atomic_Number':[], 'Electronegativity':[], 'Boiling_Point':[]}
        element_scraper = PeriodicTableScraper(n=5, root=root, list=[], features=features)
        element_scraper.extract_data()
        actual_output = element_scraper.features
        expected_output = {'Element_Name': ['Hydrogen', 'Helium', 'Lithium', 'Beryllium', 'Boron'], 
                           'Atomic_Number': ['1', '2', '3', '4', '5'], 
                           'Electronegativity': ['2.2 (Pauling Scale)', '4.16 (Allen Scale)', '0.98 (Pauling Scale)', '1.57 (Pauling Scale)', '2.04 (Pauling Scale)'],
                           'Boiling_Point': ['20.28 K (-252.87°C or -423.17°F)', '4.22 K (-268.93°C or -452.07°F)', '1615 K (1342°C or 2448°F)',  '2744 K (2471°C or 4480°F)', '4273 K (4000°C or 7232°F)']}
        self.assertCountEqual(expected_output, actual_output)

unittest.main(argv=[''], verbosity=2, exit=False)








# %%
