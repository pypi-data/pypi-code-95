NUMS = ('number', 'float', 'int', 'numstr')


def infer_dp_type(some):
    return ('numstr' if some.isnumeric() else 'str') \
        if isinstance(some, str) \
        else type(some).__name__


def infer_vector_type(column):
    if not column: return 'none'
    typeset = {*[infer_dp_type(x) for x in column]}
    if (hi := len(typeset)) == 1: return typeset.pop()
    elif hi == 2: return 'numstr' \
        if typeset.pop() in NUMS and typeset.pop() in NUMS \
        else 'misc'
    else: return 'misc'
