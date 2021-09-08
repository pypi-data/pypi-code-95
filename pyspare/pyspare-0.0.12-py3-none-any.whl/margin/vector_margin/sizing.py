from veho.vector import length


def sizing(vec, head, tail):
    size = length(vec)
    if not size: head, tail = 0, 0
    elif (not head and not tail) or (head + tail >= size): head, tail = size, 0
    return head, tail
