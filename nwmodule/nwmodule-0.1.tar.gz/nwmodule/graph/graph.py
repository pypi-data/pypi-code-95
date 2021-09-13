import torch as tr
import torch.nn as nn
import torch.optim as optim
from functools import partial
from copy import copy
from overrides import overrides
from typing import Dict, List, Set, Generator, Optional

from .draw_graph import drawGraph
from .graph_serializer import GraphSerializer
from .message import Message
from .node import Node
from .edge import Edge
from ..nwmodule import NWModule
from ..utilities import isType, npGetData, Debug, trDetachData

# A Graph is a list of Edges. Each edge is a FeedForward network between two nodes.
class Graph(NWModule):
	def __init__(self, edges, hyperParameters={}):
		self.edges = edges
		self.nodes = self.getNodes()
		hyperParameters = self.getHyperParameters(hyperParameters)
		super().__init__(hyperParameters=hyperParameters)

		self.edges = nn.ModuleList(self.getEdges())
		# (A, B) => Edge(A, B)
		self.edgeLosses = {k : [] for k in self.edges}
		self.serializer = GraphSerializer(model=self)

	@overrides
	# trInputs::Dict[str, tr.Tensor]
	# #trLabels::Dict[str, tr.Tensor]
	def networkAlgorithm(self, trInputs, trLabels, isTraining:bool, isOptimizing:bool):
		if isOptimizing:
			self.clearLosses()

		Debug.log(3, "[Graph::networkAlgorithm] Passing through all the edges for 1 iteration.")
		nodeMessages = self.forward(trInputs, numIterations=1)
		graphLoss = 0
		if isOptimizing:
			self.edgeLosses, graphLoss = self.graphBackProp(trLabels)
			self.updateOptimizer(graphLoss, isTraining, isOptimizing)
		return nodeMessages, graphLoss

	def addGTToNodes(self, data):
		# Add potential GT messages, if any.
		for node in self.nodes:
			if not node.name in data:
				continue
			# Both input and output are the same tensor, with the "GT" path. 
			message = Message(["GT"], data[node.name], data[node.name])
			node.addMessage(message)

	def messagePass(self):
		for edge in self.edges:
			A, B = edge.getNodes()
			for message in A.getMessages():
				y = edge.forward(message.output)
				newMessagePath = [*message.path, edge]
				newMessage = Message(newMessagePath, message.output, y)
				B.addMessage(newMessage)

	def aggregate(self):
		for node in self.nodes:
			node.aggregate()

	# @brief The forward pass/message passing of a graph. The algorithm is as follows:
	#  - x represents the "external" data of this passing
	#  - each forward call will send all possible messages of each node to all possible neightbours
	#  - x[node] is the new data (if it exists) for this node. Otherwise, only messages from the previous pass are used
	#  - After all the iterations are done, a reduce call is issued, which, for each node reduces the messages to a
	#  potential less number of messages.
	def forward(self, x, numIterations:int=1):
		self.clearMessages()
		self.addGTToNodes(x)
		for i in range(numIterations):
			self.messagePass()
		self.aggregate()
		y = self.getNodeMessages()
		return y

	def graphBackProp(self, trLabels):
		Debug.log(3, "[Graph::graphBackProp] Computing node losses.")
		edgeLosses = {k : [] for k in self.edges}
		nodeMessages = self.getNodeMessages()
		for node in self.nodes:
			for msg in node.getMessages():
				path, x, y = msg.path, msg.input, msg.output
				# GT node, no possible backprop
				if len(path) == 0 or (len(path) == 1 and path[-1] == "GT"):
					continue
				edge = path[-1]
				assert isinstance(edge, Edge)
				assert edge.getNodes()[1] == node
				# This edge has no criterion, skipping
				if edge.getCriterion() is None:
					continue
				assert node.name in trLabels, "%s vs %s" % (node.name, trLabels.keys())
				t = trLabels[node.name]
				l = edge.getCriterion()(y, t)
				edgeLosses[edge].append(l)
		Debug.log(3, "[Graph::graphBackProp] Passed through all nodes.")

		Debug.log(3, "[Graph::graphBackProp] Computing graph loss.")
		graphLoss = self.getCriterion()(edgeLosses)
		Debug.log(3, "[Graph::graphBackProp] Computed graph loss.")
		return edgeLosses, graphLoss

	@overrides
	def trainGeneratorNumSteps(self, generator:Generator, numSteps:int, numEpochs:int, \
		validationGenerator:Optional[Generator]=None, validationNumSteps:int=0):
		from .graph_trainer import GraphTrainer
		return GraphTrainer(self).train(generator, numSteps, numEpochs, validationGenerator, validationNumSteps)

	def clearMessages(self):
		Debug.log(3, "[Graph::clearMessages] Clearing node messages.")
		for node in self.nodes:
			node.clearMessages()

	def getNodeMessages(self) -> List[Message]:
		return {k : k.getMessages() for k in self.nodes}

	def clearLosses(self):
		Debug.log(3, "[Graph::clearLosses] Clearing edge losses.")
		# Generic container of all losses for all edges of this graph.
		self.edgeLosses = {k : [] for k in self.edges}

	def getEdges(self) -> List[Edge]:
		edges = []
		for edge in self.edges:
			edges.append(edge)
		return edges

	def getNodes(self) -> Set[Node]:
		nodes = set()
		nameToNodes = {}
		for edge in self.edges:
			A, B = edge.getNodes()
			nodes.add(A)
			nodes.add(B)
			if A.name in nameToNodes:
				assert nameToNodes[A.name] == A
			if B.name in nameToNodes:
				assert nameToNodes[B.name] == B
			nameToNodes[A.name] = A
			nameToNodes[B.name] = B
		return nodes

	def draw(self, fileName, cleanup=True, view=False):
		drawGraph(self.nodes, self.edges, fileName, cleanup, view)

	# We also override some methods on the Network class so it works with edges as well.

	@overrides
	def setOptimizer(self, optimizer, **kwargs):
		print("[Graph::setOptimizer] Settings the optimizer '%s' for all edges. This might overwrite optimizers!" % \
			optimizer)
		# assert isinstance(optimizer, type), "TODO For more special cases: %s" % type(optimizer)
		for edge in self.edges:
			if edge.getNumParams()[1] == 0:
				print("[Graph::setOptimizer] Skipping edge '%s' as it has no trainable parameters!" % edge)
				continue
			edge.setOptimizer(optimizer, **kwargs)

	@overrides
	def updateOptimizer(self, trLoss, isTraining:bool, isOptimizing:bool, retain_graph=False):
		if trLoss is None:
			return
		if not isTraining or not isOptimizing:
			trLoss.detach_()
			return

		for edge in self.edges:
			if edge.getOptimizer():
				edge.getOptimizer().zero_grad()
		trLoss.backward(retain_graph=retain_graph)
		for edge in self.edges:
			if edge.getOptimizer():
				edge.getOptimizer().step()

	@overrides
	def getOptimizerStr(self):
		strList = super().getOptimizerStr()
		for edge in self.edges:
			strEdge = str(edge)
			if type(edge) == Graph:
				strEdge = "SubGraph"
			edgeStrList = edge.getOptimizerStr()
			strList.extend(edgeStrList)
		return strList

	# @overrides
	# def metricsSummary(self):
	# 	summaryStr = super().metricsSummary()
	# 	for edge in self.edges:
	# 		strEdge = str(edge)
	# 		if type(edge) == Graph:
	# 			strEdge = "SubGraph"
	# 		lines = edge.metricsSummary().split("\n")[0 : -1]
	# 		if len(lines) > 0:
	# 			summaryStr += "\t- %s:\n" % (strEdge)
	# 			for line in lines:
	# 				summaryStr += "\t%s\n" % (line)
	# 	return summaryStr

	# @overrides
	# def callbacksSummary(self):
	# 	summaryStr = super().callbacksSummary()
	# 	for edge in self.edges:
	# 		strEdge = str(edge)
	# 		if type(edge) == Graph:
	# 			strEdge = "SubGraph"
	# 		lines = edge.callbacksSummary()
	# 		if len(lines) == 0:
	# 			continue
	# 		summaryStr += "\n\t- %s:\n\t\t%s" % (strEdge, lines)
	# 	return summaryStr

	def getHyperParameters(self, hyperParameters):
		# Set up hyperparameters for every node
		hyperParameters = {k : hyperParameters[k] for k in hyperParameters}
		for node in self.nodes:
			hyperParameters[node.name] = node.hyperParameters
		for edge in self.edges:
			hyperParameters[str(edge)] = edge.hyperParameters
		return hyperParameters

	def graphStr(self, depth=1):
		Str = "Graph:"
		pre = "\t" * depth
		for edge in self.edges:
			if type(edge) == Graph:
				edgeStr = edge.graphStr(depth + 1)
			else:
				edgeStr = str(edge)
			Str += "\n%s-%s" % (pre, edgeStr)
		return Str

	def __str__(self) -> str:
		return self.graphStr()