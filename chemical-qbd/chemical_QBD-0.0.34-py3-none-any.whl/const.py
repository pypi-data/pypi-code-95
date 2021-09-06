"""
https://pubchem.ncbi.nlm.nih.gov/periodic-table/#view=list
"""
import json
import os

cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))

file = open('elementary__data.json')
data = json.load(file)
file.close()

CHEMICAL__ELEMENTS = [element['Cell'][1] for element in data['Table']['Row']]
CHEMICAL__ELEMENTS__1 = [i for i in CHEMICAL__ELEMENTS if len(i) == 1]
CHEMICAL__ELEMENTS__2 = [i for i in CHEMICAL__ELEMENTS if len(i) == 2]

CHEMICAL__ELEMENTS__CONFIGURATION = {}
for element in data['Table']['Row']:
    CHEMICAL__ELEMENTS__CONFIGURATION[element['Cell'][1]] = element['Cell'][5]


