from tkinter import Canvas
from commind.core.node import Node
from commind.v.arrange import *
from commind.v.render import render as renderCanvas

class Engine:
    def __init__(self,canvas:Canvas):
        self.root = Node()
        self.current = self.root
        self.canvas = canvas
        self.base_pos = (512,384)
        self.pos = self.base_pos

    def exec(self,cmd:str):
        clist = cmd.split()
        if len(clist) > 0:
            cmd = clist[0]
            if cmd == 'a':
                _node = Node(parent=self.current)
                self.current.child.append(_node)
                self.current = _node
            elif cmd == 'n':
                _node = Node(parent=self.current)
                self.current.child.append(_node)
            elif cmd == 'd':
                _node = self.current
                self.current = self.current.parent
                self.current.child.remove(_node)
            elif cmd == 's':
                if len(clist)==2:
                    self.current.setText(clist[1])
            elif cmd == 'b':
                if self.current!=self.root:
                    self.current = self.current.parent
            elif cmd == 'e':
                if len(self.current.child) > 0:
                    self.current = self.current.child[0]
            elif cmd == 'l':
                _i = self.current.parent.child.index(self.current)
                if _i < len(self.current.parent.child)-1:
                    self.current = self.current.parent.child[_i+1]
                else:
                    self.current = self.current.parent.child[0]
        self.refresh()

    def refresh(self):
        arrangeNodeByRectangle(self.root)
        _c = self.current
        self.pos = self.base_pos
        while _c!=None:
            self.pos = (self.pos[0]-_c.pos[0],self.pos[1]-_c.pos[1])
            _c = _c.parent
        renderCanvas(self.canvas,self.pos,self.root)