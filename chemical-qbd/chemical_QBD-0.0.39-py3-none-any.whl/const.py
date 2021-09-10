"""
https://pubchem.ncbi.nlm.nih.gov/periodic-table/#view=list
"""
import json
import os

full_path = os.path.realpath(__file__)
file = open(os.path.dirname(full_path) + '/elementary__data.json')
data = json.load(file)
file.close()

CHEMICAL__ELEMENTS = [element['Cell'][1] for element in data['Table']['Row']]
CHEMICAL__ELEMENTS__1 = [i for i in CHEMICAL__ELEMENTS if len(i) == 1]
CHEMICAL__ELEMENTS__2 = [i for i in CHEMICAL__ELEMENTS if len(i) == 2]

CHEMICAL__ELEMENTS__CONFIGURATION = {}
for element in data['Table']['Row']:
    CHEMICAL__ELEMENTS__CONFIGURATION[element['Cell'][1]] = element['Cell'][5]


