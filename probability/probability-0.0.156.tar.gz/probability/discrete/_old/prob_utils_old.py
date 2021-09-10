from pandas import merge, Series
from typing import List

from probability.discrete.prob_utils import _match_codes

"""
The following methods assume that the distribution is represented as follows.
- The distribution is a pandas Series.
- The columns of the index are named after the variables in the distribution.
- The rows of the the index contain each unique combination of values of the 
  variables in the distribution.
- The name of the Series is 'p'.
- The values of the Series represent the probability of the combination of 
  variable values in the associated index row.
"""


def margin(distribution: Series, *margins) -> Series:
    """
    Marginalize the distribution over the variables not in args, leaving the
    marginal probability of args.

    :param distribution: The probability distribution to marginalize
                         e.g. P(A,B,C,D).
    :param margins: Names of variables to put in the margin
                    e.g. 'C', 'D'.
    :return: Marginalized distribution e.g. P(C,D).
    """
    return distribution.to_frame().groupby(list(margins))['p'].sum()


comparator_symbols = {
    'eq': lambda arg, val: f'{arg}={val}',
    'ne': lambda arg, val: f'{arg}≠{val}',
    'lt': lambda arg, val: f'{arg}<{val}',
    'gt': lambda arg, val: f'{arg}>{val}',
    'le': lambda arg, val: f'{arg}≤{val}',
    'ge': lambda arg, val: f'{arg}≥{val}',
    'in': lambda arg, vals: '{}∈{}'.format(
        arg, '{' + ",".join([str(val) for val in vals]) + '}'
    ),
    'not_in': lambda arg, vals: '{}∉{}'.format(
        arg, '{' + ",".join([str(val) for val in vals]) + '}'
    )
}


def cond_name(name_comparator: str, var_names: List[str] = None) -> str:
    """
    Return the conditioning variable name from the name and comparator code.

    :param name_comparator: Amalgamation of variable name and filtering
                            comparator in the form '{name}__{comparator}'.
    :param var_names: List of valid variables names to look for in
                      `name_comparator`.
    """
    if var_names is not None:
        if name_comparator in var_names:
            return name_comparator
    for code in _match_codes:
        if name_comparator.endswith('__' + code):
            return name_comparator[:-len('__' + code)]
    return name_comparator


def cond_name_and_symbol(
        name_comparator: str, value, var_names: List[str]
) -> str:
    """
    Return the conditioning variable name and mathematical symbol from the name
    and comparator code.

    :param name_comparator: Amalgamation of variable name and filtering
                            comparator in the form '{name}__{comparator}'.
    :param var_names: List of valid variables names to look for in
                      `name_comparator`.
    :param value: Value to filter to.
    """
    for var_name in var_names:
        for code in _match_codes:
            if var_name + '__' + code == name_comparator:
                return comparator_symbols[code](var_name, value)
    if name_comparator in var_names:
        return f'{name_comparator}={value}'


def condition(distribution: Series, *cond_vars) -> Series:
    """
    Condition the distribution on given and/or not-given values of the
    variables.

    :param distribution: The probability distribution to condition
                         e.g. P(A,B,C,D).
    :param cond_vars: Names of variables to condition over every value of
                      e.g. 'C'.
    :return: Conditioned distribution. Filtered to only given values of the
             cond_values. Contains a stacked Series of probability distributions
             for each combination of conditioning variable values
             e.g. P(A,B|C,D=d1), P(A,B|C,D=d2) etc.
    """
    col_names = distribution.index.names
    var_names = ([
        n for n in col_names
        if n not in cond_vars
    ])
    var_names.extend([n for n in col_names if n in cond_vars])
    data = distribution.copy().reset_index()
    cond_vars = list(cond_vars)
    if cond_vars:
        # find total probabilities for each combination of unique values in the
        # conditional variables e.g. P(C)
        sums = data.groupby(cond_vars).sum().reset_index()
        # normalize each individual probability e.g. p(Ai,Bj,Ck,Dl) to
        # probability of its conditional values p(Ck)
        sums = sums[cond_vars + ['p']].rename(columns={'p': 'p_sum'})
        merged = merge(left=data, right=sums, on=cond_vars)
        merged['p'] = merged['p'] / merged['p_sum']
        data = merged[var_names + ['p']]
    return data.set_index(var_names)['p']


def multiply(conditional: Series, marginal: Series) -> Series:
    """
    Multiply a conditional distribution by a marginal distribution to give a
    joint distribution.

    :param conditional: The conditional distribution e.g. P(a|b)
    :param marginal: The marginal distribution e.g. P(b)
    :return: The joint distribution e.g. P(a,b)
    """
    marginal_vars = marginal.index.names
    non_marginal_vars = [v for v in conditional.index.names
                         if v not in marginal_vars]
    cond_data = conditional.copy().rename('p_cond').to_frame().reset_index()
    joint_data = marginal.copy().rename('p_joint').to_frame().reset_index()
    merged = merge(left=cond_data, right=joint_data, on=marginal_vars)
    merged['p'] = merged['p_cond'] * merged['p_joint']
    results = merged.groupby(non_marginal_vars + marginal_vars)['p'].sum()
    return results
