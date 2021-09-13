import json
import archijson.geometry as geometry

class ArchiJSON:
    def __init__(self, data=None):
        if(type(data) == str):
            data = json.loads(data)

        try:
            self.properties = data['properties']
            self.geometryElements = data['geometryElements']
        except Exception:
            self.properties = {}
            self.geometryElements = []

        if(type(self.properties) == str):
            self.properties = json.loads(self.properties)
        if(type(self.geometryElements) == str):
            self.geometryElements = json.loads(self.geometryElements)

        self.parse_geometry()
    

    def parse_geometry(self):
        self.geometries = []
        for el in self.geometryElements:
            geom = self.__from_element(el)
            self.geometries.append(geom)


    def __from_element(self, obj):
        if(obj['type'] == 'Mesh'):
            v = geometry.call['Vertices'](**obj['vertices'])
            f = geometry.call['Faces'](**obj['faces'])
            del obj['faces']
            del obj['vertices']
            return geometry.call['Mesh'](v, f, **obj)

        elif (geometry.call[obj['type']].is_valid(obj)):
            return geometry.call[obj['type']](**obj)
    
    
    @property
    def data(self):
        return {
            'properties': self.properties,
            'geometries': self.geometries
        }
    
    def toJSON(self):
        for geom in self.geometries:
            if(geometry.call[geom.type].is_valid(geom.data)):
                self.geometryElements.append(geom.data)
            else:
                raise ValueError('Invalid geometry')
        return {
            'properties': self.properties,
            'geometryElements': self.geometryElements
        }
        
        
    def __str__(self):
        return "ArchiJSON: {}".format(json.dumps(self.data, indent = 4))


