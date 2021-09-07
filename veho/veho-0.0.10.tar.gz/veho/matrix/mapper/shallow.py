from typing import List


def shallow(mat: List[list]):
    return [vec[:] for vec in mat]

# return [x for x in vec]
# return copy.copy(vec)
