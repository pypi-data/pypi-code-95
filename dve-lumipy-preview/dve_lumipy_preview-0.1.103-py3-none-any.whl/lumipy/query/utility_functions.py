from functools import reduce
from lumipy.query.expression.table_op.row_set_op import RowSetOp

"""
Utility functions for constructing queries that augment the fluent syntax. 
"""


def concat(sub_qrys, filter_duplicates=True) -> RowSetOp:
    """Vertical concatenation of subqueries. This is the lumipy equivalent of pandas.concat()

    Args:
        sub_qrys:
        filter_duplicates:

    Returns:
        RowSetOp: object representing the union of all the subqueries.
    """
    if filter_duplicates:
        return reduce(lambda x, y: x.union(y), sub_qrys)
    else:
        return reduce(lambda x, y: x.union_all(y), sub_qrys)