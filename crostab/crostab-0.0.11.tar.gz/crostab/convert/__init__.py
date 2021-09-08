from veho.object import select_values, values, keys

from veho.vector import mapper

from crostab import Crostab


def samples_to_crostab(sample_collection, side=None, head=None):
    samples = select_values(sample_collection, *side) if side else values(sample_collection)
    crostab_side = side if side else keys(sample_collection)
    crostab_head = head if head else keys(samples[0]) if len(samples) else []
    rows = mapper(samples, (lambda sample: select_values(sample, *head)) if head else values)
    return Crostab(crostab_side, crostab_head, rows)
