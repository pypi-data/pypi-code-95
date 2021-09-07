def swap(vec, i, j):
    vec[i], vec[j] = vec[j], vec[i]
    return vec[j]


def swap_beta(vec, i, j):
    temp = vec[i]
    vec[i] = vec[j]
    vec[j] = temp
    return temp
