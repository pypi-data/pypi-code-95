from requests import get
from re import search as re_search
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from traceback import print_exc
from string import ascii_uppercase
from termcolor import colored

from WikiFiller.lib.Category import WikiCategory

def chemspider_fetch(name: str) -> str:
    if not name:
        return ""
    try:
        response = get(f'http://www.chemspider.com/Search.aspx?q={name}')
        if not response.history:
            if "0 results" in response.text:
                print(f"Chemspider fetch failed for {name}, {response.history}")
                return ""
            else:
                code = BeautifulSoup(response.text, 'html.parser').find_all('div', {"class":"results-wrapper table"})
                link = code[0].find_all('tbody')[0].find_all('tr')[0].find_all('td')[0].find_all('a')[0]['href']
                chemspider = re_search(r'\d+', urlparse(link).path)
                return chemspider.group() if chemspider else ""
        else:
            code = BeautifulSoup(response.history[0].text, 'html.parser')
            link = code.find_all('a')[0]
            chemspider = urlparse(link['href']).path.split('.html')[0].split('.')[-1]
            return chemspider
    except Exception as E:
        print(E)
        print_exc()

def chebi_fetch(name: str) -> str:
    if not name:
        return ""
    match_string = "Sorry, no results"
    try:
        r = get(f'https://www.ebi.ac.uk/chebi/advancedSearchFT.do?searchString={name}')
        code = r.text
        if match_string in code:
            print("ChEBI fetch failed")
            return ""
        """ List of pages link else direct page """
        if not r.history:
            link = BeautifulSoup(code, 'html.parser').find_all('a', {'target': '_top'})[-1]
            chebi = urlparse(link['href']).query.split(':')[-1]
        else:
            chebi = urlparse(r.url).query.split(':')[-1]
        return chebi
    except Exception as E:
        print(E)
        print_exc()

def fix_molecular(formula: str) -> list:
    organics = tuple(ascii_uppercase)
    organic_present = [elem for elem in organics if elem in formula]
    start = []
    for elem_i, elem in enumerate(organic_present):
        initial_index = None
        final_index = None
        for letter_i, letter in enumerate(formula):
            if elem == letter:
                initial_index = letter_i
            else:
                if (elem_i + 1) < len(organic_present):
                    if organic_present[int(elem_i + 1)] == letter:
                        final_index = letter_i
                        break
                else:
                    final_index = None
        start.append((elem, initial_index, final_index))
    new_start = []
    for l in start:
        elem, initial, final = l[0], l[1], l[2]
        if final:
            unfixed = formula[initial:final]
        else:
            unfixed = formula[initial:]
        fixed_element, element_atom = elem, unfixed.split(elem)[-1]
        new_start.append((fixed_element, element_atom))
    return(new_start)

def wiki_molecular(element_list: list) -> str:
    l = []
    for elem in element_list:
        elem, number = elem[0], elem[1]
        wiki_like = f"{elem} = {number}"
        l.append(wiki_like)
    return " | ".join(l)

def category_filter(type_categories_list):
    mega_list = []
    for type_categories in type_categories_list:
        for category_key in type_categories.keys():
            sub_category, description, super_category_allowed = type_categories[category_key]
            user = input(f"Does this category {colored(category_key, color='red', attrs=['bold'])} ({description}) fit inside article (Y/N)? ")
            if user.upper() == "Y":
                to_add = WikiCategory(category_key, sub_category).output
                mega_list.extend([cat_tuple[0] for cat_tuple in to_add if cat_tuple[-1]])
                if super_category_allowed:
                    mega_list.append(category_key)
    return "\n".join(f'[[Category:{c}]]' for c in set(mega_list))
