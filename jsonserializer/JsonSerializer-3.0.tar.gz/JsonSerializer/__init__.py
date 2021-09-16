import json
from typing import Any

def Serialize(value: object):
    return json.dumps(value.__dict__)

def Deserialize(text: str,obj:Any):
    obj.__dict__.update(json.loads(text))
    return obj
