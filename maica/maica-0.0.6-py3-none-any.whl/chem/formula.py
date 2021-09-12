"""
Chemical Formula
----------------
A collection of functions to convert the string of the chemical formulas into
the machine-readable numerical representations.
"""


import numpy
import ast
from maica.chem.base import atom_nums


def form_to_vec(form: str,
                elem_feats: numpy.ndarray):
    """
    Convert a given chemical formula in ``form`` into a feature vector.
    For a set of computed atomic features :math:`S = \{\mathbf{h} = f(e) | e \in c \}`
    where :math:`c` is the given chemical formula, the feature vector is calculated as a concatenated vector based on
    weighted sum with a weight :math:`w_\mathbf{h}`, standard deviation :math:`\sigma`, and max operation as:

    .. math::
        \mathbf{x} = \sum_{\mathbf{h} \in S} w_\mathbf{h} h \oplus \sigma(S) \oplus \max(S).

    Note that the standard deviation :math:`\sigma` and the max operations are applied feature-wise (not element-wise).
    This formula-to-vector conversion method is common in chemical machine learning
    [`1 <https://pubs.acs.org/doi/abs/10.1021/acs.jpclett.8b00124>`_,
    `2 <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.93.115104>`_,
    `3 <https://www.nature.com/articles/s41524-021-00564-y>`_].

    :param form: (*str*) Chemical formula (e.g., ZnIn2S4).
    :param elem_feats: (*numpy.ndarray*) The NumPy array of elemental features.
    :return: A feature vector of the chemical formula.
    """

    wt_sum_feats = numpy.zeros(elem_feats.shape[1])
    list_atom_feats = list()

    # Convert the refined chemical formula to a dictionary of the chemical formula.
    elems = ast.literal_eval(form)
    sum_elem_nums = numpy.sum([float(elems[e]) for e in elems])

    # Get atomic features for each element.
    for e in elems:
        atom_feats = elem_feats[atom_nums[e] - 1, :]
        list_atom_feats.append(atom_feats)
        wt_sum_feats += (float(elems[e]) / sum_elem_nums) * atom_feats

    # Generate a feature vector of the formula based on the weighted sum, std., and max. of the atomic features.
    form_vec = numpy.hstack([wt_sum_feats, numpy.std(list_atom_feats, axis=0), numpy.max(list_atom_feats, axis=0)])

    return form_vec


def form_to_sparse_vec(form: str,
                       elem_feats: numpy.ndarray,
                       max_elems: int):
    """
    Convert a given chemical formula in ``form`` into a feature vector.
    For a set of computed atomic features :math:`S = \{\mathbf{h} = f(e) | e \in c \}`
    where :math:`c` is the given chemical formula, the feature vector is calculated as a concatenated vector of the atomic features.
    If the number of elements is less than ``max_elems``, a zero vector is concatenated to fill the empty values.
    Thus, it always returns the feature vector with the same dimension based on ``max_elems``
    regardless of the number of elements in the chemical formula.

    :param form: (*str*) Chemical formula (e.g., ZnIn2S4).
    :param elem_feats: (*numpy.ndarray*) The NumPy array of elemental features.
    :param max_elems: (*int*) The maximum number of elements in the chemical formula.
    :return: A feature vector of the chemical formula.
    """

    # The number of features = the number of elemental features + ratio of the atom in the formula.
    form_feats = list()
    elems = ast.literal_eval(form)

    # Get atomic features for each element.
    for e in elems:
        form_feats.append(float(elems[e]))
        form_feats.append(elem_feats[atom_nums[e] - 1, :])

    # Fill zero vectors to the empty features.
    form_feats.append(numpy.zeros((max_elems - len(elems)) * (elem_feats.shape[1] + 1)))

    # Generate a sparse feature vector of the given chemical formula.
    form_feats = numpy.hstack(form_feats)

    return form_feats


def parse_form(form: str):
    """
    Parse the chemical formula to an element-wise dictionary.
    For example, ZnIn2S4 is converted into a dictionary of {Zn: 1.0, In: 2.0, S: 4.0}.

    :param form: (*str*) Chemical formula (e.g., ZnIn2S4).
    :return: An element-wise dictionary of the chemical formula.
    """

    form_dict = dict()
    elem = form[0]
    num = ''

    # Convert the chemical formula to a dictionary of the chemical formula.
    for i in range(1, len(form)):
        if form[i].islower():
            elem += form[i]
        elif form[i].isupper():
            if num == '':
                form_dict[elem] = 1.0
            else:
                form_dict[elem] = float(num)

            elem = form[i]
            num = ''
        elif form[i].isnumeric() or form[i] == '.':
            num += form[i]

        if i == len(form) - 1:
            if num == '':
                form_dict[elem] = 1.0
            else:
                form_dict[elem] = float(num)

    # Return a dictionary of {element: ratio} pairs.
    return form_dict
