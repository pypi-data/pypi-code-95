from .sizing import sizing
from .vector_margin import VectorMargin


def vector_margin(vec, head, tail, read, rule):
    return VectorMargin \
        .build(vec, head, tail) \
        .stringify(read) \
        .to_list(rule)
