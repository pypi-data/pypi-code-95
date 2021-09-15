from typing import Union

import numpy as np


class DesignVariable:
    """ A DesignVariable class for optimization purposes
    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 xs: Union[int, float],
                 variable: str,
                 bcs: str) -> None:
        """ A DesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param xs: starting value of a design variable
        :param variable: name of a design variable
        :param bcs: block index, range of indices (with -) or no block indication for global variables
        """
        self.xl = xl
        self.xu = xu
        self.xs = xs
        self.variable = variable
        try:
            bcs = str(int(bcs))
        except ValueError:
            bcs = str(bcs)
        self.bcs = bcs

    def get_variable_names(self) -> list:
        """ Method returning a design variable name. There are three output types
        - if bcs string is empty, then the variable name is returned - for global design variables
        - if bcs string contains a dash, then the range of indices is considered
        - if bcs string contains a number, then the variable:bcs name is returned
        - otherwise, an AttributeError is raised

        :return: a list of strings with variable names
        """
        if self.bcs == '' or self.bcs == 'nan':
            return [self.variable]
        elif '-' in self.bcs:
            return self._convert_range_of_blocks_into_list()
        elif self.bcs.isnumeric():
            return ["%s:%s" % (self.bcs, self.variable)]
        else:
            raise AttributeError('The design variable has incorrect block index value: %s.' % self.bcs)

    def _convert_range_of_blocks_into_list(self) -> list:
        bcs_ranges = self.bcs.split('-')
        if len(bcs_ranges) != 2:
            raise AttributeError('The block index range definition %s is wrong. Only one hyphen is allowed.' % self.bcs)

        if not bcs_ranges[0].isnumeric():
            raise AttributeError('The lower block index range %s is not a number.' % bcs_ranges[0])

        if not bcs_ranges[1].isnumeric():
            raise AttributeError('The upper block index range %s is not a number.' % bcs_ranges[1])

        lower = int(bcs_ranges[0])
        upper = int(bcs_ranges[1])

        if lower > upper:
            raise AttributeError('The lower index %d is greater than the upper one %d.' % (lower, upper))

        return ['%d:%s' % (block, self.variable) for block in range(lower, upper + 1)]


class GeneticDesignVariable(DesignVariable):
    """ A DesignVariable class for genetic optimization purpose

    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 xs: Union[int, float],
                 variable: str,
                 bcs: str,
                 variable_type: str,
                 bits: int) -> None:
        """ A GeneticDesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param xs: starting value of a design variable
        :param variable: name of a design variable
        :param bcs: block index, range of indices (with -) or no block indication for global variables
        :param variable_type: variable type (int, float) used to determine the gene to value conversion type
        :param bits: the number of bits to represent a design variable
        """
        if variable_type == 'int':
            super().__init__(int(xl), int(xu), int(xs), variable, bcs)
        else:
            super().__init__(float(xl), float(xu), float(xs), variable, bcs)
        self.bits = bits
        self.variable_type = variable_type

    def generate_random_gene(self) -> list:
        """ Method generating a random gene for int and float design variables

        :return:
        """
        gene = list(np.random.randint(0, 2, self.bits))
        if self.variable_type == 'float':
            return gene
        elif self.variable_type == 'int':
            gene_int = GeneticDesignVariable.convert_gene_to_int(gene)
            if gene_int > (self.xu - self.xl):
                gene_temp = GeneticDesignVariable.convert_int_to_gene(self.xu - self.xl)
                return (self.bits - len(gene_temp)) * [0] + gene_temp
            else:
                return gene
        else:
            raise AttributeError('The variable type %s should be either int or float.' % self.variable_type)

    def convert_gene_to_value(self, gene: list) -> Union[int, float]:
        """ Method converting a gene to design variable value (either int or float):
        - for int, the value is given as lower limit + gene integer value; in case of an overflow, the upper limit is
        considered
        - for float, the value is given as the lower limit + gene integer value multiplied by variable range and divided
        by the number of binary combinations

        :param gene: a list of bits representing a design variable
        :return: numeric value of a gene
        """
        gene_int = GeneticDesignVariable.convert_gene_to_int(gene)

        # convert to value
        if self.variable_type == 'int':
            return min(int(self.xl + gene_int), int(self.xu))
        else:
            return self.xl + gene_int * (self.xu - self.xl) / 2 ** self.bits

    @staticmethod
    def convert_gene_to_int(gene: list) -> int:
        """ Static method converting a gene as a list into an integer

        :param gene: a list of bits representing a gene
        :return: an integer value of a gene
        """
        # convert chromosome to a string of chars
        gene_chars = ''.join([str(s) for s in gene])

        # convert string to integer
        return int(gene_chars, 2)

    @staticmethod
    def convert_int_to_gene(n: int) -> list:
        """ Static method converting an integer to a gene

        :param n: an integer value of a gene
        :return: a list of bits representing a gene
        """
        return [n >> i & 1 for i in range(n.bit_length() - 1, -1, -1)]


class CockpitGeneticDesignVariable(GeneticDesignVariable):

    def __init__(self, gen_dv: "GeneticDesignVariable") -> None:
        super().__init__(**gen_dv.__dict__)
        self.logger_column = self.get_minimal_logger_column_name()
        self.variable_name = self.get_variable_name_for_widget_bar_plot()

    def get_minimal_logger_column_name(self) -> str:
        if '-' in self.bcs:
            return '%s:%s' % (self.bcs.split('-')[0], self.variable)
        elif self.bcs == 'nan' or self.bcs == '':
            return self.variable
        else:
            return '%s:%s' % (self.bcs, self.variable)

    def get_variable_name_for_widget_bar_plot(self) -> str:
        if '-' in self.bcs:
            return '%s:%s' % (self.bcs, self.variable)
        elif self.bcs == 'nan' or self.bcs == '':
            return self.variable
        else:
            return '%s:%s' % (self.bcs, self.variable)

    def get_hover_text(self, value):
        if self.variable_type == 'float':
            return 'value: %.3f, range: [%.3f, %.3f]' % (value, self.xl, self.xu)
        else:
            return 'value: %d, range: [%d, %d]' % (value, self.xl, self.xu)

    def get_fraction(self, value):
        return (value - self.xl) / (self.xu - self.xl)
