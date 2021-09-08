import math

def mathematical_operations():

        def __init__(self, expression):
            """Делим пользовательское выражение на отдельные
            составляющие: два числа и знак"""
            try:
            	self.output = eval(expression)
                return self.output
            except:
            	self.first_number = expression.split()[0]
            	self.sign = expression.split()[1]
            	self.second_number = expression.split()[2]

def arithmetic_operations():

    def addition(first_term, second_term):
        return first_term + second_term

    def multiplication(first_multiplier, second_multiplier):
        return first_multiplier * second_multiplier

    def subtraction(minuend, subtrahend):
        return minuend - subtrahend

    def division(dividend, divider):
        if dividend // divider == dividend/divider:
            return dividend // divider
        else:
            return dividend / divider

def binary_operations():
    pass

def output():

	def console_arithmetic_output(self, us_expression):
	    try:
	    	return Mathematical_operations(us_expression).output
	    except:
		    if self.sign == "+":
		        return Arithmetic_operations.addition(
		        int(self.first_number), int(self.second_number))
		    if self.sign == "*":
		        return Arithmetic_operations.multiplication(
		        int(self.first_number), int(self.second_number))
		    if self.sign == "-":
		        return Arithmetic_operations.subtraction(
		        int(self.first_number), int(self.second_number))
		    if self.sign == ":":
		        return Arithmetic_operations.division(
		        int(self.first_number), int(self.second_number))

__author__ = "SoftwareDebug"
__version__ = "0.0.1"
__email__ = "zodiakraft@gmail.com"
