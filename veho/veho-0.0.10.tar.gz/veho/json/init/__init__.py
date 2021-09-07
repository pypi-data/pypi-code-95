import json


def iso(vec: list, val):
    lex = {k: val for k in vec}
    return json.dumps(lex)


def dict_to_json(lex: dict):
    return json.dumps(lex)


def json_to_dict(jso: json):
    return json.loads(jso)
