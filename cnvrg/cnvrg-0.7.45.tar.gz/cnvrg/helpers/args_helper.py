from cnvrg.modules.errors import CnvrgError

def args_to_string(args):
    if args == None: return ''
    if isinstance(args, list): args = {k["key"]: k.get("value") for k in args}
    ### expect dict of key=value
    return " ".join(map(lambda x: k_v_arg_to_string(x[0], x[1]), args.items()))

def k_v_arg_to_string(k,v):
    if v == None:
        return "--{key}".format(key=k)
    elif isinstance(v, bool) and v:
        return "--{key}".format(key=k)
    elif isinstance(v, bool) and not v:
        return "--{key}=false".format(key=k)
    elif isinstance(v, float) or isinstance(v, int):
        return "--{key}={value}".format(key=k, value=v)
    else:
        return "--{key}='{value}'".format(key=k, value=v)


def validate_args(args):
    for key,value in args.items():
        if isinstance(value, list):
            raise CnvrgError("Library local run with many arguments are not supported yet.")