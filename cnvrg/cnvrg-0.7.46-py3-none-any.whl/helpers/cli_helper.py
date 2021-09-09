import json
def parse_args(args):
    return dict(map(lambda x: x.split(":"), args))


def parse_datasets(datasets):
    parsed_datasets = []
    for dataset in datasets:
        commit = None
        dataset_slug = dataset
        if ":" in dataset:
            dataset_slug, commit = dataset.split(":")
        parsed_datasets += [{"slug": dataset_slug, "commit": commit}]
    return parsed_datasets



def __filter_o(o):
    if isinstance(o, list):
        return __remove_nones_array(o)
    if isinstance(o, dict):
        return __remove_nones_dict(o)
    return o

def __filter_bool(o):
    if o == None: return False
    if o == '': return False
    return True

def __remove_nones_dict(o):
    o_keys = filter(lambda x: __filter_bool(o[x]), o.keys())
    return {k: __filter_o(o[k]) for k in o_keys}


def __remove_nones_array(a):
    return list(filter(__filter_bool, [__filter_o(o) for o in a]))

def print_object(o, filter_nones=False):
    if filter_nones: o = __filter_o(o)
    print(json.dumps(o, sort_keys=True, indent=4))