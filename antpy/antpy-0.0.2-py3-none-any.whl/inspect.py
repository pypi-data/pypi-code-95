import inspect

def name_values(*args):
    '''
    Get names and values of passed variables

    Usage
    -------
    >> a = 1
    >> b = 2
    >> name_values(a,b)
    >> Out: {'a': 1, 'b': 2}
    '''
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    
    res = {}
    
    for var in args:
        res[str([k for k, v in callers_local_vars if v is var][0])] = var
    return res