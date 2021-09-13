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
