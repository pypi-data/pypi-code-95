from .node import Node

# @brief Generic Map Node (2D) having a number of channels (D1xD2xNC)  
class MapNode(Node):
	def __init__(self, name:str, numDims:int, hyperParameters:dict={}):
		super().__init__(name, hyperParameters)
		self.numDims = numDims