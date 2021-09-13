import schema
import json
from archijson.geometry import BaseGeometry


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


class Vertices(BaseGeometry):
    def __init__(self, coordinates, size=3, pointSize=10, **kwargs):
        if('type' in kwargs):
            del kwargs['type']
        super(Vertices, self).__init__('Vertices', **kwargs)
        self.size = size
        self.pointSize = pointSize
        self.coordinates = coordinates
    
    @staticmethod
    def DATASCHEMA():
        return schema.Schema({
            'type': 'Vertices',
            'size': schema.And(int, lambda x: x > 0),
            'coordinates': list
        }, ignore_extra_keys=True)
    
    @property
    def param(self):
        return {
            'type': 'Vertices',
            'size': self.size,
            'coordinates': self.coordinates
        }
    
    @property
    def data(self):
        return {
            **super(Vertices, self).data,
            **self.param
        }

    def toList(self):
        return list(chunks(self.coordinates, self.size))
    
    @property
    def validate(self):
        return {
            **super(Vertices, self).validate(),
            **Vertices.DATASCHEMA().validate(self.data)
        }

    @staticmethod
    def is_valid(obj):
        return BaseGeometry.DATASCHEMA().is_valid(obj) & Vertices.DATASCHEMA().is_valid(obj)



class Segments(BaseGeometry):
    def __init__(self, coordinates, size=3, closed=True, filled=False, **kwargs):
        if('type' in kwargs):
            del kwargs['type']
        super(Segments, self).__init__('Segments', **kwargs)
        self.coordinates = coordinates
        self.size = size
        self.closed = closed
        self.filled = filled

    @staticmethod
    def DATASCHEMA():
        return schema.Schema({
            'type': 'Segments',
            'size': schema.And(int, lambda x: x > 0),
            'closed': schema.Optional(bool),
            'filled': schema.Optional(bool),
            'coordinates': list
        }, ignore_extra_keys=True)
    
    @property
    def param(self):
        return {
            'closed': self.closed,
            'filled': self.filled,
            'size': self.size,
            'coordinates': self.coordinates
        }
    
    @property
    def data(self):
        return {
            **super(Segments, self).data,
            **self.param
        }
    
    @property
    def validate(self):
        return {
            **super(Segments, self).validate(),
            **Segments.DATASCHEMA().validate(self.data)
        }

    @staticmethod
    def is_valid(obj):
        return BaseGeometry.DATASCHEMA().is_valid(obj) & Segments.DATASCHEMA().is_valid(obj)
    
    def toList(self):
        return list(chunks(self.coordinates, self.size))
    


class Faces:
    def __init__(self, count=[], size=[], index=[], properties={}):
        self.type = 'Faces'
        self.count = count
        self.size = size
        self.index = index
        self.properties = properties
    
    @staticmethod
    def DATASCHEMA():
        return schema.Schema({
            'type': 'Faces',
            'count': [int],
            'size': [int],
            'index': [int],
            schema.Optional('properties'): dict
        })

    @staticmethod
    def is_valid(obj): 
        return Faces.DATASCHEMA().is_valid(obj)

    @property
    def validate(self):
        return Faces.DATASCHEMA().validate(self.data)
    
    @property
    def data(self):
        return {
            'type': self.type,
            'count': self.count,
            'size': self.size,
            'index': self.index,
            'properties': self.properties,
        }
    
    def __str__(self):
        return ("{}: {}".format(self.type, json.dumps(self.data, indent = 4)))
    
    def toList(self):
        ret, lst = [], 0
        for i, cnt in enumerate(self.count):
            sz = self.size[i]
            ret.extend(list(chunks(self.index[lst:lst+sz*cnt], sz)))
            lst += sz * cnt
        return ret


class Mesh(BaseGeometry):
    def __init__(self, vertices, faces, **kwargs):
        if('type' in kwargs):
            del kwargs['type']
        super(Mesh, self).__init__('Mesh', **kwargs)
        self.vertices = vertices
        self.faces = faces
    
    @property
    def param(self):
        return {
            'vertices': self.vertices.param,
            'faces': self.faces.data,
        }
    
    @property
    def data(self):
        return {
            **super(Mesh, self).data,
            **self.param
        }



    @property
    def validate(self):
        return {
            **super(Mesh, self).validate(),
            'vertices': self.vertices.validate,
            'faces': self.faces.validate
        }

    @staticmethod
    def is_valid(obj):
        return BaseGeometry.DATASCHEMA().is_valid(obj) & Vertices.DATASCHEMA().is_valid(obj['vertices']) & Faces.DATASCHEMA().is_valid(obj['faces'])
