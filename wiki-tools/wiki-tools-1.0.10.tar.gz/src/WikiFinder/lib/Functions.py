from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from pubchempy import get_compounds, BadRequestError, TimeoutError

def get_name_from_cid(cid):
    url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
    compound_data = BeautifulSoup(get(url).text, 'html.parser')
    title = compound_data.find_all("meta", {"property":"og:title"})
    if title:
        title = title[0].attrs['content']
    else:
        title = ""
    return title

def change_molecular(molecular_list: list, atom_changes: list = []) -> list:
    if not atom_changes:
        changed_list = ["".join(changable) for changable in molecular_list]
        return changed_list

    atom_dict = {elem[0]: elem[1] for elem in molecular_list}
    for atom_change in atom_changes:
        atom_type, atom_name, atom_number = atom_change[0], atom_change[1], atom_change[2]
        if atom_type == "+":
            if atom_name in atom_dict:
                new_atom_number = str(int(atom_dict[atom_name]) + int(atom_number))
                atom_dict[atom_name] = new_atom_number
            else:
                new_atom_number = str(atom_number)
                atom_dict[atom_name] = new_atom_number
        elif atom_type == "_":
            if atom_name in atom_dict:
                new_atom_number = str(int(atom_dict[atom_name]) - int(atom_number))
                if int(new_atom_number) != 0:
                    atom_dict[atom_name] = new_atom_number
                else:
                    atom_dict.pop(atom_name)
    atom_dict = dict(sorted(atom_dict.items()))
    new_list = []
    for a,n in list(atom_dict.items()):
        joined = "".join((a,n)) if int(n) != 1 else a
        new_list.append(joined)
    return new_list

def fix_molecular(formula: str) -> list:
    from string import ascii_uppercase
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
    return new_start

def get_smiles_from_nist(url):
    if not url:
        return url
    r = BeautifulSoup(get(url).text, 'html.parser')
    #name = r.find_all('h1', {'id':'Top'})[0].string
    inchi = r.find_all('span', {'clss':'inchi-text'})
    if not inchi:
        return "", ""
    inchi = inchi[0].string
    smiles = get_compounds(inchi, 'inchi')[0].canonical_smiles
    return smiles

def new_molecular_formula_fetch_nist(molecular_formula: str) -> dict:
    if not molecular_formula:
        return {}
    try:
        compounds = get_compounds(molecular_formula, 'formula')
    except BadRequestError:
        return {}
    except TimeoutError:
        return {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_objects = [executor.submit(get_name_from_cid, compound.cid) for compound in compounds]
    names = [future_object.result() for future_object in future_objects]
    compounds_all = dict(zip(names, compounds))
    return compounds_all

def molecular_formula_fetch_nist(molecular_formula: str) -> dict:
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?Formula={molecular_formula}&NoIon=on&Units=SI"
    r = BeautifulSoup(get(url).text, 'html.parser')
    if not molecular_formula or "Not found" in r.find_all('title')[0].string:
        return {}
    #compounds = [print(elem, type(elem)) for elem in r.find_all('ol')]
    compounds = [elem.findChildren("a") for elem in r.find_all('ol')][0]
    """ Change into threads later """
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_objects = [executor.submit(get_smiles_from_nist, f"https://webbook.nist.gov{compound['href']}") for compound in compounds]
    smiles = [future_object.result() for future_object in future_objects]
    names = [compound.string for compound in compounds]
    links = dict(zip(names, smiles))
    return links
        #print(elem)
        #print(type(elem.findChildren("a")))
        #breakpoint()
    #breakpoint()
    # url = f"https://webbook.nist.gov/cgi/cbook.cgi?Formula={molecular_formula}&NoIon=on&Units=SI"
    # r = BeautifulSoup(get(url).text, 'html.parser')
    # if not molecular_formula or 'Not Found' in r.find_all('title')[0].string:
        # return []
    # compounds_links = [elem.findChildren("a") for elem in r.find_all('ol')[0]]
    # compounds = [elem.findChildren("a") for elem in r.find_all('ol')][0]
    # compounds_everything = [(get_name_from_cid(compound.cid), compound) for compound in compounds]
    # links = [f"https://webbook.nist.gov{compound['href']}" for compound in compounds]
    # compounds_all = [get_names_inchi_from_nist(link) for link in links]
    # compounds_all = [c for c in compounds_all if c[0] and c[1]]
    # names_smiles = [(c[0], get_compounds(c[1], 'inchi')[0].canonical_smiles) for c in compounds_all]
    # breakpoint()
    # return

# def molecular_formula_fetch_wiki(molecular_formula: str) -> list:
    # url = f'https://en.wikipedia.org/wiki/{molecular_formula}'
    # response = get(url)
    # r = BeautifulSoup(response.text, 'html.parser')
    # if not molecular_formula or 'Wikipedia does not have an article' in response.text:
        # return []
    # if not molecular_formula in r.find_all('title')[0].string:
        # return []
    # compound_li = r.find_all('div', {'class':'mw-parser-output'})[0].find_all('li')
    # titles = [l.find_all('a', {"title":True}) for l in compound_li]
    # final_titles = [t[0]['title'] for t in titles if t]
    # href = [l.find_all('a', {"href":True})[0]['href'].split('/wiki')[-1] for l in compound_li]
    # final_href = [h for h in href if not '#' in h]
#     return ["".join(f) for f in zip(final_titles, final_href)]
