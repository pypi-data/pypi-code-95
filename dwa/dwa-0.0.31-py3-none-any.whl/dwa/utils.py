__ALL__ = ["parse_params"]


def parse_params(items):
    params = dict(items)
    for k, v in params.items():
        params[k] = [_.decode() if isinstance(_, bytes) else _ for _ in v]
    return params

