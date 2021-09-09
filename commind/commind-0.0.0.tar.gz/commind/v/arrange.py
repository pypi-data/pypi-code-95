
from commind.core.node import Node

#region is a length mutable list 

def arrangeNodeByRectangle(node:Node):
    node.region = [-node.shape[0],-node.shape[1],node.shape[0],node.shape[1]]
    node.pos = (0,0)
    for i in node.child:
        arrangeNodeByRectangle(i)
    _height = 0
    for i in node.child:
        _height = _height + i.region[3] - i.region[1]
        i.pos = (node.region[2]-i.region[0],_height-i.region[3])
    _height = _height / 2
    for i in node.child:
        i.pos = (i.pos[0],i.pos[1]-_height)
    for i in node.child:
        node.region[0] = min(node.region[0],i.region[0]+i.pos[0])
        node.region[1] = min(node.region[1],i.region[1]+i.pos[1])
        node.region[2] = max(node.region[2],i.region[2]+i.pos[0])
        node.region[3] = max(node.region[3],i.region[3]+i.pos[1])
