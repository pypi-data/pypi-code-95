from typing import Dict
import ujson
import falcon


def read_stream(stream):
    _stream = stream.read().decode()
    if not _stream:
        raise falcon.HTTPBadRequest("Bad request", "JSON body is required")
    try:
        data = ujson.loads(_stream)
        return data
    except Exception as e:
        raise falcon.HTTPBadRequest("Bad request", "JSON body is broken")


def check_dict_attr(attr, data: Dict, error: str):
    try:
        data = attr(**data)
        return data
    except TypeError as e:
        raise falcon.HTTPBadRequest("Bad request", error)
    except ValueError as e:
        raise falcon.HTTPBadRequest("Bad request", error)


def write_to_file(path: str, data, mode: str):
    temp_file = open(path, mode, encoding="utf-8")
    if type(data) is str:
        temp_file.write(data)
    temp_file.close()


def read_file(path: str) -> str:
    with open(path, encoding='utf-8', mode='r') as f:
        lines = f.readlines()
        data = ''
        for line in lines:
            data += line
    return data
