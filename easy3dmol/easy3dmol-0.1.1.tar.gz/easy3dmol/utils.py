import time
import random
import inspect

def retrieve_name(var):
    '''
    get back the name of variables
    Currently useless...
    '''
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

def seed():
    return time.strftime("%Y%m%d%H%M%S", time.localtime()) + str(random.randint(10, 99))

def random_name():
    return "".join(random.sample('zyxwvutsrqponmlkjihgfedcba',5)+random.sample("1234567890",5))