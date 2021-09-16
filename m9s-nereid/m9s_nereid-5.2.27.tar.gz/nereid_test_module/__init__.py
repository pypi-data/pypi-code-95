# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.pool import Pool
from . import model


def register():
    """
    This function will register test nereid module
    """
    Pool.register(
        model.TestModel,
        module='nereid_test', type_='model',
    )
