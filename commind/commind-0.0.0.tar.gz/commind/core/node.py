
from commind.core.style import Style
from commind.core.nodecontent import NodeContent

class Node:
    def __init__(self,parent=None,text='text',style='{}'):
        self.style = Style(style)
        self.content = NodeContent(text)
        self.parent = parent
        self.child = []
        self.pos = (0,0)
        self.shape = (len(text)*14,14)
        self.region = [0,0,0,0]

    def setText(self,text):
        self.content.text = text
        self.shape = (len(text)*14,14)

    def setImage(self,image):
        self.content.image = image

