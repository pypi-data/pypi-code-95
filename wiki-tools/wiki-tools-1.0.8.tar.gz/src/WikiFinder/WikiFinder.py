#!/usr/bin/python3
from bs4 import BeautifulSoup
from requests import get
from argparse import ArgumentParser
from pubchempy import get_compounds
from fuzzywuzzy import fuzz
from operator import itemgetter
from pyperclip import copy as clipboard_copy

#from WikiFinder.lib.Browser import Browser
from WikiFinder.lib.Functions import change_molecular, fix_molecular
from WikiFinder.lib.Functions import molecular_formula_fetch_nist
#from WikiFinder.lib.Functions import molecular_formula_fetch_wiki

# from lib.Functions import change_molecular, fix_molecular
# from lib.Functions import molecular_formula_fetch

def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', '--molecular-formula', type=str, help="Outputs list of chemicals from molecular formula")
    group.add_argument('-n', '--name', type=str, help="Ouputs list of chemicals matching compound molecular formula from name")
    parser.add_argument('-c', '--change', default=[], nargs='*', help="Enter atom change of compound using spaces. '+' increases atom while '_' decreases. Eg -c '_C1' '+H3'")
    parser.add_argument('-o', '--output', type=str, help="Enter output filename")
    argv = parser.parse_args()

    if not argv.molecular_formula and not argv.name:
        print("Use --help")
        exit()

    #browser_driver = Browser()
    #browser_driver.driver.get(url)

    #def molecular_formula_from_name(name):
        #url = f'https://pubchem.ncbi.nlm.nih.gov/compound/{name}'
        #compound_data = BeautifulSoup(get(url).text, 'html.parser')

        #title = compound_data.find_all("meta", {"property":"og:title"})[0].attrs['content']
        #molecular_formula = change_molecular(fix_molecular(browser_driver.find_element_by_id(By.ID,"Molecular-Formula").upper()), argv.change)
        #return molecular_formula
    compound = {
        'name': '',
        'compound': '',
        'formula': '',
        'smiles': '',
    }
    if argv.name:
        compound['name'] = argv.name
        compound['compound'] = get_compounds(argv.name, 'name')[0]
        compound['smiles'] = compound['compound'].canonical_smiles
        compound['formula'] = change_molecular(fix_molecular(compound['compound'].molecular_formula), argv.change)
        #molecular_formula = molecular_formula_from_name(argv.name)
    else:
        compound['formula'] = change_molecular(fix_molecular(argv.molecular_formula), argv.change)
    compound['formula'] = "".join(compound['formula'])

    compounds_nist = molecular_formula_fetch_nist(compound['formula'])
    #compounds_wiki = molecular_formula_fetch_wiki(molecular_formula)
    #final_compounds = compounds_nist + compounds_wiki
    final_compounds = []
    if compound['smiles']:
        for name, smile in list(compounds_nist.items()):
            n = fuzz.ratio(compound['smiles'], smile)
            final_compounds.append((name, smile, n))
        final_compounds.sort(key = itemgetter(-1), reverse=True)
        final_compounds = [f"{name}:{smile}" for name,smile,n in final_compounds]
    else:
        final_compounds = list(compound_nist.keys())
    compounds = "\n".join(final_compounds)
    if compound['smiles']:
        s = f"Printing compounds with same {compound['formula']} sorted by most similar matching smile {compound['smiles']}"
    else:
        s = f"Printing compounds with same {compound['formula']}"
    print(s)
    print(compounds)

    clipboard_copy(compounds)
    #browser_driver.driver.quit()

    if argv.output:
        with open(argv.output, 'w+') as f:
            f.write(compounds)

if __name__ == '__main__':
    main()
