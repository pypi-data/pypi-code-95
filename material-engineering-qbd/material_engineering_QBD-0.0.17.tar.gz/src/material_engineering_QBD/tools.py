import chemical_QBD
from . import numeric
import units_QBD

# from material_engineering_QBD.chemical_QBD import const
# from . import chemical_QBD
# from . import numeric
# from . import units_QBD
# from . import numpy

def read__sheet(sheet: str, unit:str):
    """
    Returns list of materials and thickness from sheet
    """
    rows = sheet.split('\n')
    rows = [i for i in filter(None, rows)]
    for i in range(0,len(rows)):
        comment__position = rows[i].find('#')
        if comment__position == -1: continue
        else: rows[i] = rows[i][:comment__position]
    rows = [i for i in rows if ' ' in i]

    rows__materials = []
    rows__thicknesses = []

    for row in rows:
        break__position = row.find(' ')
        row = row[:break__position] + row[break__position:].replace(' ', '')

        # Angstorm shortcut, not Amper
        if row.endswith('A'):   row = row[:-1] + 'Angs'

        if numeric.isfloat(row[break__position:]): row = row + unit

        value, unit_ = units_QBD.standardise__statement(row[break__position:])

        material = [c for c in row[:break__position] if c.isalpha()]

        material_ = ''
        for i in material:  material_ += i

        if chemical_QBD.is__consisted__of__chemical__elements(material_):
            rows__materials.append(row[:break__position])
            rows__thicknesses.append(value)
    
    return rows__materials, rows__thicknesses








def interpolation__exception(material: str, parameters: dict, bowings: dict):
    """
    Require 0.12 (ratios everywhere) CO2, 
    no spaces
    prepared
    """
    elements__count = material.count('.')
    if   elements__count == 0: return None
    elif elements__count == 1: return parameters[material[:material.find('.')]]
    elif elements__count == 2: return interpolation__exception__AB(material, parameters, bowings)
    elif elements__count == 3: return interpolation__exception__ABC(material, parameters, bowings)
    elif elements__count == 4: return interpolation__exception__ABCD(material, parameters, bowings)

        


def interpolation__exception__AB(material: str, parameters: dict, bowings: dict):
    """
    C0.2Si0.8
    C.5Ge.5
    """
    dot__A = material.find('.')
    dot__B = material.find('.', dot__A + 1)
    
    fraction__A__ended = dot__A
    while not material[fraction__A__ended].isalpha(): fraction__A__ended += 1

    material__A = material[:dot__A]
    material__B = material[fraction__A__ended:dot__B]

    fraction__A = float(material[dot__A:fraction__A__ended])
    fraction__B = float(material[dot__B:])

    return fraction__A * parameters[material__A] + fraction__B * parameters[material__B] - fraction__A * fraction__B * float(bowings[material__A + material__B])

def interpolation__exception__ABC(material: str, parameters: dict, bowings: dict):
    """
    Al0.3Ga0.7As1.0
    Ga.2In.8Sb.0
    """
    dot__A = material.find('.')
    dot__B = material.find('.', dot__A + 1)
    dot__C = material.find('.', dot__B + 1)

    fraction__A__ended = dot__A
    fraction__B__ended = dot__B

    while not material[fraction__A__ended].isalpha(): fraction__A__ended += 1
    while not material[fraction__B__ended].isalpha(): fraction__B__ended += 1

    fraction__A = float(material[dot__A:fraction__A__ended])
    fraction__B = float(material[dot__B:fraction__B__ended])
    fraction__C = float(material[dot__C:])

    element__A = material[:dot__A]
    element__B = material[fraction__A__ended:dot__B]
    element__C = material[fraction__B__ended:dot__C]

    composition = element__A + element__B + element__C

    if fraction__A == .0:   return fraction__B * parameters[element__A + element__B] + fraction__C * parameters[element__A + element__C] - fraction__B * fraction__C * float(bowings[composition])
    elif fraction__C == .0: return fraction__A * parameters[element__A + element__C] + fraction__B * parameters[element__B + element__C] - fraction__A * fraction__B * float(bowings[composition])
    else:
        material__11 = element__A + str(fraction__C / 2.)[1:]
        material__12 = element__B + str(1 - fraction__C / 2.)[1:]
        part__1 = fraction__A * fraction__B * interpolation__exception(material__11 + material__12, parameters, bowings)

        material__21 = element__B + str(fraction__C - 0.5 * fraction__A)[1:]
        material__22 = element__C + str(1 - fraction__C + 0.5 * fraction__A)[1:]
        part__2 = fraction__B * fraction__C * interpolation__exception(material__21 + material__22, parameters, bowings)
        
        material__31 = element__A + str(fraction__C - 0.5 * fraction__B)[1:]
        material__32 = element__C + str(1 - fraction__C + 0.5 * fraction__B)[1:]
        part__3 = fraction__A * fraction__C * interpolation__exception(material__31 + material__32, parameters, bowings)

        denominator = fraction__A * fraction__B + fraction__A * fraction__C + fraction__B * fraction__C
        return (part__1 + part__2 + part__3) / denominator


def interpolation__exception__ABCD(material: str, parameters: dict, bowings: dict):
    """
    Al0.3Ga0.7As1.0
    Ga.2In.8Sb.0
    """
    dot__A = material.find('.')
    dot__B = material.find('.', dot__A + 1)
    dot__C = material.find('.', dot__B + 1)
    dot__D = material.find('.', dot__C + 1)

    fraction__A__ended = dot__A
    fraction__B__ended = dot__B
    fraction__C__ended = dot__C

    while not material[fraction__A__ended].isalpha(): fraction__A__ended += 1
    while not material[fraction__B__ended].isalpha(): fraction__B__ended += 1
    while not material[fraction__C__ended].isalpha(): fraction__C__ended += 1

    fraction__A = float(material[dot__A:fraction__A__ended])
    fraction__B = float(material[dot__B:fraction__B__ended])
    fraction__C = float(material[dot__C:fraction__C__ended])
    fraction__D = float(material[dot__D:])

    element__A = material[:dot__A]
    element__B = material[fraction__A__ended:dot__B]
    element__C = material[fraction__B__ended:dot__C]
    element__D = material[fraction__C__ended:dot__D]

    if fraction__A == .0:
        material__11 = element__A + '.0'
        material__12 = element__B + str(.5 * fraction__D)[1:]
        material__13 = element__C + str(1 - 0.5 * fraction__D)[1:]
        part__1 = fraction__B * fraction__C * interpolation__exception(material__11 + material__12 + material__13, parameters, bowings)

        material__21 = element__A + '.0'
        material__22 = element__C + str(fraction__D - .5 * fraction__B)[1:]
        material__23 = element__D + str(1 - fraction__D + .5 * fraction__B)[1:]
        part__2 = fraction__C * fraction__D * interpolation__exception(material__21 + material__22 + material__23, parameters, bowings)
        
        material__31 = element__A + '.0'
        material__32 = element__B + str(fraction__D - .5 * fraction__C)[1:]
        material__33 = element__D + str(1 - fraction__D + .5 * fraction__C)[1:]
        part__3 = fraction__B * fraction__D * interpolation__exception(material__31 + material__32 + material__33, parameters, bowings)

        denominator = fraction__B * fraction__C + fraction__B * fraction__D + fraction__C * fraction__D
        return (part__1 + part__2 + part__3) / denominator
        
    elif fraction__D == .0:
        material__11 = element__A + str(.5 * fraction__C)[1:]
        material__12 = element__B + str(1 - .5 * fraction__C)[1:]
        material__13 = element__D + '.0'
        part__1 = fraction__A * fraction__B * interpolation__exception(material__11 + material__12 + material__13, parameters, bowings)

        material__21 = element__B + str(fraction__C - .5 * fraction__A)[1:]
        material__22 = element__C + str(1 - fraction__C + .5 * fraction__A)[1:]
        material__23 = element__D + '.0'
        part__2 = fraction__B * fraction__C * interpolation__exception(material__21 + material__22 + material__23, parameters, bowings)
        
        material__31 = element__A + str(fraction__C - .5 * fraction__B)[1:]
        material__32 = element__C + str(1 - fraction__C + .5 * fraction__B)[1:]
        material__33 = element__D + '.0'
        part__3 = fraction__A * fraction__C * interpolation__exception(material__31 + material__32 + material__33, parameters, bowings)

        denominator = fraction__A * fraction__B + fraction__A * fraction__C + fraction__B * fraction__C
        return (part__1 + part__2 + part__3) / denominator
        
    else:
        material__11 = element__A + str(fraction__A)[1:]
        material__12 = element__B + str(fraction__B)[1:]
        material__13 = element__D + '.0'
        part__1 = fraction__A * fraction__B * fraction__D * interpolation__exception(material__11 + material__12 + material__13, parameters, bowings)

        material__21 = element__A + str(fraction__A)[1:]
        material__22 = element__B + str(fraction__B)[1:]
        material__23 = element__C + '.0'
        part__2 = fraction__A * fraction__B * fraction__C * interpolation__exception(material__21 + material__22 + material__23, parameters, bowings)
        
        material__31 = element__A + '.0'
        material__32 = element__C + str(fraction__C)[1:]
        material__33 = element__D + str(fraction__D)[1:]
        part__3 = fraction__A * fraction__C * fraction__D * interpolation__exception(material__31 + material__32 + material__33, parameters, bowings)
        
        material__41 = element__B + '.0'
        material__42 = element__C + str(fraction__C)[1:]
        material__43 = element__D + str(fraction__D)[1:]
        part__4 = fraction__B * fraction__C * fraction__D * interpolation__exception(material__41 + material__42 + material__43, parameters, bowings)

        denominator = fraction__A * fraction__B + fraction__C * fraction__D
        return (part__1 + part__2 + part__3 + part__4) / denominator







def profile__plain(thicknesses, values):
    ground = [0.]
    fence = [values[0]]

    for i in range(0,len(thicknesses) - 1):
        ground.append(thicknesses[i])
        fence.append(values[i])

        ground.append(thicknesses[i])
        fence.append(values[i + 1])

    ground.append(thicknesses[-1])
    fence.append(values[-1])

    return ground, fence

