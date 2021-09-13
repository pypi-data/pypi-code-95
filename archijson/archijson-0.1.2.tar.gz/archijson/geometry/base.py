import uuid
import schema
import json

def identity(n):
    arr = [0. for i in range(n*n)]
    for i in range(n):
        arr[i*n+i] = 1.
    return arr
    

class BasePoint():

    def DATASCHEMA():
        return schema.Schema({
            'x': schema.Or(float, int),
            'y': schema.Or(float, int),
            'z': schema.Or(float, int)
        })

    def __init__(self, x=0, y=0, z=0):
        if((type(x) == dict) and BasePoint.is_valid(x)):
            self.x = x['x']
            self.y = x['y']
            self.z = x['z']
        elif((type(x) == tuple) or (type(x) == list)):
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        elif((type(x) == BasePoint) and BasePoint.is_valid(x.data)):
            self.x = x.x
            self.y = x.y
            self.z = x.z
        else:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)

    def __str__(self):
        return ("Point: x = {}, y = {}, z = {}".format(self.x, self.y, self.z))

    def validate(self):
        return BasePoint.DATASCHEMA().validate(self.data)

    def is_valid(obj):
        return BasePoint.DATASCHEMA().is_valid(obj)


    @property
    def data(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z
        }

class BaseGeometry():

    def DATASCHEMA():
        return schema.Schema({
            'type': str,
            'uuid': str,
            'matrix': schema.And(list, lambda x: len(x) == 16),
            schema.Optional('properties'): dict,
            'position': BasePoint.DATASCHEMA(),
        }, ignore_extra_keys=True)

    def __init__(self, type, uuid=str(uuid.uuid4()), matrix=identity(4), properties={}, position=BasePoint(),  **kwargs):
        self.type = type
        self.uuid = uuid
        self.matrix = matrix
        self.properties = properties
        self.__position = BasePoint(position)

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        p = BasePoint(position)

        self.matrix[12] = p.x
        self.matrix[13] = p.y
        self.matrix[14] = p.z
        self.__position = p

    def __str__(self):
        return ("{}: {}".format(self.type, json.dumps(self.data, indent = 4)))

    def validate(self):
        return BaseGeometry.DATASCHEMA().validate(self.data)

    @property
    def data(self):
        return {
            'type': self.type,
            'uuid': self.uuid,
            'matrix': self.matrix,
            'properties': self.properties,
            'position': self.position.data,
        }
