"""
https://pubchem.ncbi.nlm.nih.gov/periodic-table/#view=list
"""
import json
  
file = open('elementary__data.json')
data = json.load(file)
file.close()