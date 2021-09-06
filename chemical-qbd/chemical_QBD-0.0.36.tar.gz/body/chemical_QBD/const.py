"""
https://pubchem.ncbi.nlm.nih.gov/periodic-table/#view=list
"""
import json

# cwd = os.getcwd()  # Get the current working directory (cwd)
# files = os.listdir(cwd)  # Get all the files in that directory
# print("Files in %r: %s" % (cwd, files))

import os

# print("Path at terminal when executing this file")
# print(os.getcwd() + "\n")

# print("This file path, relative to os.getcwd()")
# print(__file__ + "\n")

# print("This file full path (following symlinks)")
full_path = os.path.realpath(__file__)
# print(full_path + "\n")

# print("This file directory and name")
# path, filename = os.path.split(full_path)
# print(path + ' --> ' + filename + "\n")

print("This file directory only")
print(os.path.dirname(full_path))


file = open(os.path.dirname(full_path) + '/elementary__data.json')
data = json.load(file)
file.close()

CHEMICAL__ELEMENTS = [element['Cell'][1] for element in data['Table']['Row']]
CHEMICAL__ELEMENTS__1 = [i for i in CHEMICAL__ELEMENTS if len(i) == 1]
CHEMICAL__ELEMENTS__2 = [i for i in CHEMICAL__ELEMENTS if len(i) == 2]

CHEMICAL__ELEMENTS__CONFIGURATION = {}
for element in data['Table']['Row']:
    CHEMICAL__ELEMENTS__CONFIGURATION[element['Cell'][1]] = element['Cell'][5]


