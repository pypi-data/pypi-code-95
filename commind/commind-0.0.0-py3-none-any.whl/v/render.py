import tkinter
from commind.core.node import Node

def render(canvas:tkinter.Canvas,pos,node:Node):
    canvas.delete(tkinter.ALL)
    
    def _render(_pos,_node:Node):
        _delta_x = _pos[0]+_node.pos[0]
        _delta_y = _pos[1]+_node.pos[1]
        for i in _node.child:
            _render((_delta_x,_delta_y),i)
            canvas.create_line(_delta_x,_delta_y,_delta_x+i.pos[0],_delta_y+i.pos[1])
        canvas.create_rectangle(_node.region[0]+_delta_x,_node.region[1]+_delta_y,_node.region[2]+_delta_x,_node.region[3]+_delta_y)
        canvas.create_text(_delta_x,_delta_y,text=_node.content.text)
    
    _render(pos,node)

    