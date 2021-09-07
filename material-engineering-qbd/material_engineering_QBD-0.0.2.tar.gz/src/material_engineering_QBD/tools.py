import chemical_QBD
from . import numeric
import units_QBD

def read_sheet(sheet: str, unit:str):
    """
    Returns list of materials and thickness from sheet
    """
    rows = sheet.split('\n')
    rows = [i for i in filter(None, rows)]
    rows = [i for i in rows if ' ' in i]

    rows__materials = []
    rows__thicknesses = []

    for row in rows:
        break__position = row.find(' ')

        # Angstorm shortcut, not Amper
        if row.endswith('A'):   row = row[:-1] + 'Angs'

        value, unit = units_QBD.standardise__statement(row[break__position:])

        material = [c for c in row[:break__position] if c.isalpha()]
        if chemical_QBD.is__consisted__of__chemical__elements(material):
            rows__materials.append(row[:break__position])
            rows__thicknesses.append(value)
    
    return rows__materials, rows__thicknesses
