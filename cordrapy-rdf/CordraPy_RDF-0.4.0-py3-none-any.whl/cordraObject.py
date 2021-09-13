# Standard Library packages
from uuid import uuid4
from typing import Dict
import json
from copy import deepcopy

# Other Libraries
import fastjsonschema


def rdfDefault(o):
   if isinstance(o, CordraObject):
       return o.properties.get("@id")


class CordraObject:
    _prefix: str #URL
    _schema: Dict=dict()
    _jsonDefault = staticmethod(rdfDefault)

    def __new__(cls, **kwargs):
        cls.validate = staticmethod(fastjsonschema.compile(cls._schema))

        return super().__new__(cls)

    
    def __init__(self, properties, payloads=None): 
        # Set defaults on properties
        self.properties = dict()

        for k, v in self._schema["properties"].items():
            if "default" in v:
                self.properties[k] = v["default"]

        self.properties.update(properties)

        # self.validate(self.properties)

        self.payloads = payloads


    def json(self):
        return json.dumps(self.properties, default=self._jsonDefault)

    # TODO
    # def fromJSON(self, j, p=[]):
    #     self.properties = json.loads(j)
    #     self.payloads = p