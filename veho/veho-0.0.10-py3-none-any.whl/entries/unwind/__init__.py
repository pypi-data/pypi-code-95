def unwind(entries):
    return [list(tup) for tup in zip(*entries)]


def unwind_to_tuples(entries):
    return list(zip(*entries))
