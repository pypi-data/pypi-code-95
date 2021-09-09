import json
import yaml
import cnvrg.modules.errors as errors
import os

def load_hyper_search(path_to_hypersearch):
    if isinstance(path_to_hypersearch, dict): return path_to_hypersearch
    path_to_hypersearch = __hyper_path(path_to_hypersearch)
    with open(path_to_hypersearch, 'r') as f:
        if path_to_hypersearch.endswith(".yaml") or path_to_hypersearch.endswith(".yml"):
            return yaml.safe_load(f)
        if path_to_hypersearch.endswith(".json"):
            return json.load(f)
    raise errors.CnvrgError("Cant load hypersearch from {path} hypersearch should be in json or yml format".format(path=path_to_hypersearch))


def __hyper_path(path):
    if not os.path.exists(path):
        path = os.path.join(os.curdir, path)
        if not os.path.exists(path): raise errors.CnvrgError("Cant find hypersearch in {path}".format(path=path))
    return path
