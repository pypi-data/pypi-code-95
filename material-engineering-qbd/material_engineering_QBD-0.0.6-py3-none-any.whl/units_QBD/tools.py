from . import const
from . import standardise_

#### FUNCTIONS

is__operator = lambda char: char in const.OPERATORS

def power(expression, power):
    """

    Parameters:
        phrase: string
                    e.g. 'm**2*mm**-1*m*s**-1'
        power:  string
                    e.g. '-2.0' or '-1'
    Return:
        phrase: string
    Important:
        Do not use '^' character as power, only '**' are acceptable.
        Do not use any numbers in expression, except in power (m**-3.0 etc.).
        Do not use addition operations (+) or subtraction (-) or division (/).        
        Do not use ' ' characters.
    """

    expression = expression.replace('**','@@')
    elements = expression.split('*')

    for i in range(0,len(elements)):
        if '@@' in elements[i]:
            unit = elements[i].replace('@@','**')
            position = unit.find('**')
            power_ = float(unit[position + 2:])
            unit = unit[:position] + '**' + str(power_ * float(power))
            elements[i] = unit
        else:   
            elements[i] += '**' + power

    # merging
    expression = ''
    for i in elements:  expression += '*' + i
    if expression.startswith('*'):  expression = expression[1:]

    return expression
    
def plain__reduction(expression):
    '''
    Executes operations '*' and '**' without a sort.

    Parameters:
    expression: string
                e.g. 'mm*A*Hz**2*J**-1' 

    Returns:
    value:      float
                0.001
    expression: string
                (from above) ???
    Important:
    No brackets
    No division operators '/'
    No '^' characters
    No ' '
    No digits, except in power
    '''

    if not '**' in expression:  return multiplication(expression)
    else:
        value = 1.
        unit = ''

        expression = expression.replace('**','@@')
        elements = expression.split('*')
        for i in range(0,len(elements)):
            element = elements[i]
            if '@@' in elements[i]:
                element = element.replace('@@','**')
                position = element.find('**')
                power_ = element[position + 2:]
                element = element[:position]
                value_, element = drop__prefix(element)
                value *= value_ ** float(power_)
                value_, element = to__basic__SI(element)
                value *= value_ ** float(power_)
                element = power(element,power_)
                elements[i] = element
            else:
                value_, element = drop__prefix(element)
                value *= value_
                value_, element = to__basic__SI(element)
                value *= value_
                elements[i] = element

        multies = ''
        powers = ''
        multies_ = [i for i in elements if '**' not in i]
        powers_  = [i for i in elements if '**' in i]
        for i in multies_:  multies += i + '*'
        for i in powers_:   powers  += i + '*'
        multies = multies[:-1]
        powers  = powers[:-1]
        if not multies == '':
            value_, multies = multiplication(multies)
            value *= value_
            return value, multies + '*' + powers
        else: return value, powers

def multiplication(expression):
    '''
    Converts multiplicaation of units SI into base units SI.

    Parameters:
    expression: string
                e.g. 'm*mm*K*A*s**-2' 

    Returns:
    expression: string
                (from above) m**2*K*C*s**-3
    value:      float
                0.001
    Important:
    No brackets
    No division operators '/'
    No '^' and '**' characters
    No ' '
    No digits, except in power
    '''

    value, unit = 1., ''

    elements = expression.split('*')

    for unit_ in elements:
        value_, unit_ = drop__prefix(unit_)
        value *= value_
        value_, unit_ = to__basic__SI(unit_)
        value *= value_

        unit += '*' + unit_
        
    return value, unit[1:]

def to__basic__SI(unit):
    '''
    Converts the unit into basic units SI.

    Parameters:
    unit:   string
            e.g. 'J', 'A', 'Hz' ... 
    Returns:
    unit:   string
            unit(s) SI
    '''
    
    if unit in const.SI:    return 1., unit
    if unit in const.SI_:   return const.SI_[unit]
    else:                   raise ValueError('\'{}\' is unknown unit'.format(unit))


def drop__prefix(unit):
    '''
    Removes prefix in the unit SI.

    Parameters
    ----------
    unit:  string
        Unit e.g. 'nm', 'mK', 'GHz'. 

    Returns
    -------
    value:  float
    unit:   string
    '''

    # if there is no anything to drop
    if unit in const.SI or unit in const.SI_:   return 1., unit

    # conversion
    if unit[:2] == 'da': 
        if unit[2:] in const.SI:    return 10., unit[2:]
        elif unit[2:] in const.SI_: return 10., unit[2:]
        else:                       raise ValueError('\'{}\' is unknown unit'.format(unit[2:]))
    else:
        if unit[:1] in const.PREFIXES:
            if unit[1:] in const.SI:    return float(const.PREFIXES[unit[:1]]), unit[1:]
            elif unit[1:] in const.SI_: return float(const.PREFIXES[unit[:1]]), unit[1:]
            else:                       raise ValueError('\'{}\' is unknown unit'.format(unit[1:]))
        else:                           raise ValueError('\'{}\' is not prefix SI'.format(unit[:1]))


def power__elementary(expression):
    '''
    Converts the expression containing single operator ** into base units SI.

    Parameters:
    expression: string
                e.g. 'J**2', 'mm**-2.0' ... 
    Returns:
    value:      float
    expression: string
    '''

    elements = expression.split('**')
    value, unit = 1., ''

    value_, elements[0] = drop__prefix(elements[0])
    value *= value_ ** float(elements[1])
    elements[0] = power(elements[0], elements[1])

    return value, elements[0]

def reductor(expression):
    '''
    Reduces unuseful elements in the expression e.g. 1.0 -> 1, J**1 ->J etc.

    Parameters:
    expression: string
                e.g. 'mm*K*J**2.0*s**1.0'
    Returns:
    expression: string
    '''

    expression = expression.replace('**', '@@')
    elements = expression.split('*')
    elements = [element.replace('@@', '**') for element in elements]

    # dictionary of units with their powers
    units = {}
    for element in elements:
        position = element.find('**')
        if position == -1:
            if element in units:    units[element] += 1
            else:                   units[element] = 1
        else:
            if element[:position] in units: units[element[:position]] += float(element[position + 2:])
            else:                           units[element[:position]] =  float(element[position + 2:])

    expression = ''
    for element in units: 
        if units[element] == 0:                             continue
        elif units[element] - round(units[element],0) == 0: expression += element + '**' + str(int(units[element])) + '*'
        else:                                               expression += element + '**' + str(units[element]) + '*'
    expression = expression[:-1]
     
    position = expression.find('**1')
    while position > -1:
        if not position + 3 == len(expression):
            if not expression[position + 3].isnumeric():    expression = expression[:position] + expression[position + 3:]
        else:   expression = expression[:position]
        position = expression.find('**1', position + 3)

    return expression

def syntax(expression):
    """
    Gives the expression with sorted units.

    Parameters:
    expression: string
                e.g. 'm*K*kg**2*s**-2'
    Return:     string
                (from above) 
    Important:
    Only '*' & '**' operators.
    No brackets
    No ' ' chars
    Only units SI and SI derived
    No prefixes
    No digits
    No the same units (one unit, one power)
    """

    expression = expression.replace('**','@@')
    elements = expression.split('*')
    elements = [element.replace('@@','**') for element in elements]

    # each unit got power
    length = len(elements)
    elements_ = []
    for i in range(0,length):
        element = elements[i]
        if '**' in element: elements_.append(element)
        else:               elements_.append(element + '**1')

    # dictionary (unit: power)
    elements = {}
    for element in elements_:
        position = element.find('**')
        elements[element[:position]] = float(element[position + 2:])

    # whether power > 0 or power < 0
    positives = {i: elements[i] for i in elements if elements[i] > 0}
    negatives = {i: elements[i] for i in elements if elements[i] < 0}

    positives = dict(sorted(positives.items(), key=lambda item: item[1]))
    negatives = dict(sorted(negatives.items(), key=lambda item: item[1],reverse=True))

    
    sorted_ = {} 

    # sorting the units with the same power
    for dic in [positives, negatives]:
        for value in dic.values():
            dictionary__one__value = {}
            for key in dic:
                if dic[key] == value: dictionary__one__value[key] = value
            dictionary__one__value = dict(sorted(dictionary__one__value.items()))
            sorted_.update(dictionary__one__value)

    # merging the final expression
    expression = ''
    for i in sorted_:   expression += i + '**' + str(sorted_[i]) + '*'

    # notation correction
    expression = reductor(expression[:-1])

    return expression


def compare__units(*argv, values=False):
    """
    Compares expression, whether given units sweeping each other.

    Parametets:
        *argv:  strings
                expressions e.g. '1/mm^3', 'm/m**4', 'cm^-3' train.
        values: bool
                considering values comparison
    Returns:   
        result: bool
                True if expressions are the same in basic units SI (and values are the same).
    """
    
    length = len(argv)
    if length == 0: raise ValueError('nothinng to compare')
    if length == 1: raise ValueError('too few expressioins')

    reduced = {}
    values_ = {}
    # dictionary of reduced expressions
    for i in argv:
        standardised = standardise_.standardise(i)
        values_[i], reduced[i] = standardised.get()

    unit = reduced[argv[0]]
    value = values_[argv[0]]

    for i in reduced.values(): 
        if not i == unit:   return False
    if values: 
        for i in values_.values(): 
            if not i == value:   return False

    return True


























def standardise__statement(expression):

    unit__position = None
    for i in range(0, len(expression)):
        if expression[i].isalpha(): 
            unit__position = i
            break

    value = float(expression[:unit__position])

    phrase = standardise_.standardise(expression[unit__position:])

    return value * phrase.value, phrase.expression