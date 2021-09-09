import json

class Style:
    def __init__(self,string_json=''):
        self.properties = json.loads(string_json)

    def __getitem__(self,key):
        _path = key.split('.')
        iter = self.properties
        for i in range(_path.length):
            iter = iter[_path[i]]
        return iter

    def __setitem__(self,key,value):
        _path = key.split('.')
        iter = self.properties
        for i in range(_path.length):
            iter = iter[_path[i]]
        iter=value