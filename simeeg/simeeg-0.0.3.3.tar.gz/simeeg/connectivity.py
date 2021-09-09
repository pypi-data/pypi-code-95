import numpy as np


def rand_tril_arr (nsize=None, overwite_val=False, kmax=None, val_rand=None):
    # create the matrix with random values
    size = 5
    arr = np.random.rand ( size, size )
    arr [np.triu_indices ( size, k=0 )] = 0
    if overwite_val:
        # set values randomly
        # val = val_rand
        # k_max = kmax
        ix = np.random.choice ( range ( int ( (size * size - size) / 2 ) ), kmax )
        rnd = np.tril_indices ( size, k=-1 )
        arr [(rnd [0] [ix], rnd [1] [ix])] = val_rand
    return arr
