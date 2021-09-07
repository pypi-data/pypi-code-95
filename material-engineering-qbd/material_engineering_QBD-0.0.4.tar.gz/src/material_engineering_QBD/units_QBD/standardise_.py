from . import tools

class standardise(object):
    """
    Converts a plain units expression into basic form SI.

    Parameters:
        expression: string
                    e.g. '1/(mm*K)**2*K / eV^-3/J**(-2)'
    Return:
        value:      float
                    (from above) 4.11...E-51
        unit:       string
                    (from above) 'K^-1kg^5m^8/s^10K'
    Notes:
        '**', '^' is the same notation of power, both acceptable. 
        Any ' ' character will not raise any bug.
        ')J*...', ')mm^2', etc. notation are acceptable.
    Important:
        Do not use any numbers in expression, except in power (m^2, m**(-3) etc.).
        Do not use addition operations (+) or subtraction (-).                    
    """
    
    get     = lambda self: (self.value, self.expression)
    show    = lambda self: print(self.value, self.expression)

    def __init__(self, expression):
        self.__expression = expression
        expression = self.__notation__corrector(expression)
        expression = self.__bracket__reduction(expression)
        expression = self.__division__reduction(expression)
        value, expression = tools.plain__reduction(expression)
        expression = tools.reductor(expression)
        expression = tools.syntax(expression)

        self.value = value
        self.expression = expression

    def __notation__corrector(self, expression):
        """
        Imposes a special notation on the expression.

        Parameters:
            expression:     string
                            e.g. '1/(mm*K)**2*K / eV^-3/J**(-2)'
        Return:
            expression:    string
                            the expression in another form
        Important:
            Do not use any numbers in expression, except in power (m^2, m**(-3) etc.).
            Do not use addition operations (+) or subtraction operations (-).                    
        """
        
        if not expression.count('(') == expression.count(')'): raise ArithmeticError('brackets error')

        expression = expression.replace(' ', '')
        expression = expression.replace('^','**')
        expression = expression.replace('(1/','(/')
        if expression.startswith('1/'): expression = expression[1:]

        # adds multiplication operator close to brackets
        i = 1
        while i < len(expression)-1:
            if expression[i] == '(' and not tools.is__operator(expression[i-1]): expression = expression[:i]   + '*' + expression[i:]
            if expression[i] == ')' and not tools.is__operator(expression[i+1]): expression = expression[:i+1] + '*' + expression[i+1:]
            i += 1

        # transits '1/' into '/', removes '1'
        expression = expression.replace('**','@@')
        expression = expression.replace('*1/', '/')
        expression = expression.replace('@@','**')

        return expression

    def __is__power(self, phrase):
        """
        Checks whether the phrase is able to be a numeric power.

        Parameters:
            phrase: string
                    e.g. '(-2.0)'
        Return:
            result: bool                    
        """
        
        if phrase.startswith('(') and phrase.endwith(')'):  phrase = phrase[1:-1]
        if phrase.startswith('-'):  phrase = phrase[1:]

        if phrase.isnumeric():  return True
        else:                   return False

    def __extract__power(self, power):
        """
        Parameters:
            power:  string
                    e.g. '(-2.0)'
        Return:
            power: float                    
        """
        if power.startswith('(') and power.endswith(')'):  power = power[1:-1]
        return float(power)

    def __bracket__reduction(self, expression):
        """
       Executes operations in the expression till brackets dispose.

        Parameters:
            expression:     string
                            e.g. '(1/mm)**(-2)/(s*Hz)'
        Return:
            expressioin:    string
                            (from above) /mm**-2*s**-1*Hz**-1
        Notes:
            '**', '^' is the same notation of power, both acceptable. 
            Any ' ' character will not raise any bug.
            ')J*...', ')mm^2', etc. notation are acceptable.
        Important:
            Do not use any numbers in expression, except in power (m^2, m**(-3) etc.).
            Do not use addition operations (+) or subtraction (-).                    
        """
        
        # each loop takes off one brackets pair

        
        while '(' in expression:
            length = len(expression)

            # finds the first pair of elementary brackets
            bracket_l = expression.find('(')
            bracket_r = expression.find(')')
            while not expression.find('(',bracket_l + 1,bracket_r) == -1: bracket_l = expression.find('(',bracket_l + 1,bracket_r)
            bracket_l_  = bracket_l + 1
            bracket_l__ = bracket_l - 1
            bracket_r_  = bracket_r + 1
            bracket_r__ = bracket_r - 1
            bracket_r___= bracket_r + 3

            # they contain a numeric power?
            if self.__is__power(expression[bracket_l_:bracket_r]): 
                expression = expression[:bracket_l] + expression[bracket_l_:bracket_r] + expression[bracket_r_:]
                continue

            # divisor?
            if expression[bracket_l__] == '/':
                if expression[bracket_r_:bracket_r___] == '**': 
                    # finding the end of power
                    position = None
                    for i in range(bracket_r___, length):
                        if tools.is__operator(expression[i]):    
                            position = i
                            break
                    if position == None:    position = length
                    power = expression[bracket_r___:position]
                    power = -self.__extract__power(power)
                    power = str(power)
                    expression = expression[:bracket_l__] + '*' + expression[bracket_l:bracket_r_] + '**' + power + expression[position:]
                    if expression.startswith('*'):    expression = expression[1:] 
                    continue
                else:
                    expression = expression[:bracket_l__] + '*' + expression[bracket_l:bracket_r_] + '**-1'
                    if expression.startswith('*'): expression = expression[1:]
                    continue

            # base of a power?
            position = None
            if expression[bracket_r_:bracket_r___] == '**': 
                for i in range(bracket_r___, length):
                    if tools.is__operator(expression[i]):
                        position = i
                        break
                if position == None:    position = length
                expression = expression[:bracket_l] + tools.power(expression[bracket_l_:bracket_r], expression[bracket_r___:position]) + expression[position:]
                continue

        return expression

    def __division__reduction(self, expression):
        """
        Swaps operator '/' into operator '**'.

        Parameters:
            expression: string
                        e.g. '/mm**-2*s*J/m**2'
        Return:
            expression: string
                        (from above) mm**2*s*J*m**-2
        Important:
            Do not use any brackets in the expression.                 
        """
        
        if not '/' in expression: return expression

        elements = expression.split('/')

        if expression.startswith('/'):  expression = ''
        else:                           expression = elements[0] + '*'
        elements = elements[1:]

        for i in range(0, len(elements)):
            element = elements[i]
            length = len(element)
            position = element.find('*')
            if position == -1:  elements[i] += '**-1'
            elif element[position + 1] == '*':
                position_ = length
                for j in range(position + 2, length):
                    if tools.is__operator(element[j]):
                        position_ = j
                        break
                power = float(element[position + 2:position_])
                elements[i] = element[:position] + '**' + str(-power) + element[position_:]
            else: elements[i] = element[:position] + '**-1' + element[position:]
        
        for i in elements:  expression += i + '*'
        return expression[:-1]
