from archijson import ArchiServer, ArchiJSON
from archijson.geometry import BasePoint
from sensitive_info import URL, TOKEN

server = ArchiServer(URL, TOKEN, 'archijson')

def on_receive(id, body):
    print(id)
    print(body)
    archijson = ArchiJSON(body)
    print(archijson.geometries)

    o = ArchiJSON()
    
    for geom in archijson.geometries:
        p = geom.position
        
        geom.position = BasePoint(p.x, p.y - 900, p.z)
        geom.uuid = ''
        o.geometries.append(geom)
        
    server.send('client', o.toJSON(), id)

server.on_receive = on_receive
