# import chemical_QBD
# from . import numeric
# import units_QBD

from . import chemical_QBD
from . import numeric
from . import units_QBD

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
        row = row[:break__position] + row[break__position:].replace(' ', '')

        # Angstorm shortcut, not Amper
        if row.endswith('A'):   row = row[:-1] + 'Angs'

        if numeric.isfloat(row[break__position:]): row = row + unit
        print(row)

        value, unit_ = units_QBD.standardise__statement(row[break__position:])

        material = [c for c in row[:break__position] if c.isalpha()]

        material_ = ''
        for i in material:  material_ += i

        if chemical_QBD.is__consisted__of__chemical__elements(material_):
            rows__materials.append(row[:break__position])
            rows__thicknesses.append(value)
    
    return rows__materials, rows__thicknesses
