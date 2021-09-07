def transpose(mx):
    return [list(tup) for tup in zip(*mx)]  # return list of list
    # return [*zip(*mx)] # returns list of tuples
