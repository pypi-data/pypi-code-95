"""
Module for calculate sum of two numbers.
"""
class Calculator(object):
    """Calculator class for calculate sum, subtract, multiply and divide.
    """
    def __init__(self):
        """Constructor for class Calculator"""

    def cal_sum(self, a, b):
        """Calculate sum of two numbers.

        Examples
        ----------
        >>> from calculator.calculate import Calculator
        >>> calculator = Calculator()
        >>> s = calculator.cal_sum(1, 2)
        """
        assert type(a) in [int, float]

        return a + b

    def cal_sub(self, a, b):
        """Calculate subtract of two numbers.

        Examples
        ----------
        >>> from calculator.calculate import Calculator
        >>> calculator = Calculator()
        >>> s = calculator.cal_sub(2, 1)
        """
        assert type(a) in [int, float]

        return a - b

    def cal_mul(self, a, b):
        """Calculate multiply of two numbers.

        Examples
        ----------
        >>> from calculator.calculate import Calculator
        >>> calculator = Calculator()
        >>> s = calculator.cal_mul(2, 3)
        """
        assert type(a) in [int, float]

        return a*b

    def cal_div(self, a, b, divide_zero=1):
        """Calculate dividision of two numbers.

        Examples
        ----------
        >>> from calculator.calculate import Calculator
        >>> calculator = Calculator()
        >>> d = calculator.cal_div(6, 3)
        """
        assert type(a) in [int, float]

        if b != 0:
            return a/b
        else:
            return divide_zero
