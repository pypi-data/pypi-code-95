'''A Dataset manages multiple cordraObjects and syncs with cordraClients'''
from .cordraClient import CordraClient
from .cordraObject import CordraObject
from uuid import uuid4

class Dataset:
    '''Dataset is an RDF specific implementation of object management'''
    def __init__(self, client, cordraObjects=[]):
        self.client = client
        self.cordraObjects = cordraObjects

        self.classes = dict()
        for name, schema in client.schemas.items():
            self.classes[name] = type(name, (CordraObject,), dict())
            self.classes[name]._schema = schema


    def add(self, name, properties=dict(), payloads=dict()):
        if name not in self.classes:
            raise KeyError('name not in client schemas')

        # Dummy ID
        properties.update({"@id": str(uuid4())})
        obj = self.classes[name](properties=properties, payloads=payloads)
        r = self.client.create(obj.properties, obj.properties["@type"], payloads=obj.payloads)
        obj.properties["@id"] = r["@id"]
        self.cordraObjects.append(obj)
        return obj


    def pull(self, obj_id):
        r = self.client.read(obj_id, full=True, getAll=True)
        obj = self.classes[r["type"]](properties=r["content"], payloads=r.get("payloads", []))
        self.cordraObjects.append(obj)
        return obj


    def rem(self, obj):
        self.cordraObjects.remove(obj)
        r = self.client.delete(obj.properties["@id"])
        return r


    def sync(self):
        for obj in self.cordraObjects:
            self.client.update(obj.properties, obj.properties["@id"])