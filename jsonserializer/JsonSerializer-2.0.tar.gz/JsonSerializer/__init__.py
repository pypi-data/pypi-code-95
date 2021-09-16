import json

def Serialize(value: object):
    return json.dumps(value.__dict__)

def Deserialize(text: str):
    obj = object()
    obj.__dict__.update(json.loads(text))
    return obj
