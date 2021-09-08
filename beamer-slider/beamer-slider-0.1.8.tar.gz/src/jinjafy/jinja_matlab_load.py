import numpy as np
import scipy.io as spio

def matlab_load(mfile):
    j = mfile.rfind('.')
    if j > -1:
        ex = mfile[j + 1:]
        base = mfile[:j]
    else:
        ex = ''
        base = mfile
    mat = loadmat(base + '.mat')
    mat = uuroll(mat)
    mat = fix_1_arrays(mat)
    mat = fix_strings(mat)
    mat = fix_simple_lists(mat)
    return mat


def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename,struct_as_record=False)
    data2 = _check_keys(data)
    return data2


def _check_keys(dd):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    if isinstance(dd, spio.matlab.mio5_params.mat_struct):
        dd = _check_keys(_todict(dd))
    elif type(dd) == dict:
        for key in dd:
            kv = flist(dd[key])
            if type( kv ) == spio.matlab.mio5_params.mat_struct:
                dd[key] = _check_keys(kv)
            else:
                dd[key] = _check_keys(dd[key])
    elif type(dd) == list:
        dd = [_check_keys(l) for l in dd]
    elif type(dd) == np.ndarray:
        if dd.dtype.str == '|O' and dd.size > 0:
            if type( flist(dd.flat[0]) ) == spio.matlab.mio5_params.mat_struct:
                for i in range( dd.size ):
                    dd.flat[i] = _check_keys( flist( dd.flat[i]) )
        else:
            for i in range(dd.size):
                dd.flat[i] = _check_keys(dd.flat[i])

    return dd

def fix_simple_lists(l):
    if type(l) == dict:
        for k,v in l.items():
            l[k] = fix_simple_lists(v)
    elif type(l) == np.ndarray and l.dtype.name == "uint8" and l.shape[0] == 1 and l.ndim == 2:
        # l = l.tolist()
        l = l.tolist()[0]
    return l

def apply_recursively(l, myfun):
    if type(l) == dict:
        for k,v in l.items():
            l[k] = apply_recursively(v, myfun)
    elif type(l) == np.ndarray and l.dtype.str == '|O' and l.size > 0:
        for i in range( l.size ):
            l.flat[i] = apply_recursively( l.flat[i], myfun)
    else:
        l = myfun(l)
    return l


def fix_1_arrays(l):
    def _fix_1_arrays(l):
        if type(l) == np.ndarray and l.size == 1 and np.issubdtype(l.dtype, np.number):
            l = l.flat[0]
        return l
    l = apply_recursively(l, _fix_1_arrays)
    return l


def fix_strings(l):
    if type(l) == dict:
        for k,v in l.items():
            l[k] = fix_strings(v)
    elif type(l) == np.ndarray and l.size > 0:
        tp = type(superpop(l.flat[0]))
        if tp == str or tp == np.str_:
            l = [superpop(x) for x in l.flat ]
            if len(l) == 1:
                l = l.pop()
    return l


def superpop(l):
    if type(l) == list and len(l) == 1:
        return superpop(l[0])
    if type(l) == np.ndarray and l.size == 1:
        return superpop(l.tolist())
    return l


def flist(l):
    if type(l) == list and len(l) == 1:
        l = flist( l.pop() )

    if type(l) == np.ndarray and l.dtype.name == "object":
        l3 = [flist(v) for v in l.flat]
        l = flist( l3 )
    return l


def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict


def uuroll(v):
    if type(v) is dict:
        for key,val in v.items():
            v[key] = uuroll(val)
    if type(v) is np.ndarray or type(v) is np.array:
        for j in range(v.size):
            v.flat[j] = uuroll(v.flat[j])
    return v


def uroll(mat):
    for k in mat.keys():
        v = mat[k]
        v = uuroll(v)
        mat[k] = v
    return mat