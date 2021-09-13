import torch as tr
import torch.nn as nn
import numpy as np
from abc import ABC, abstractmethod
from functools import partial
from collections import OrderedDict
from overrides import overrides
from typing import Dict, Optional, Tuple, Callable

from ..node import Node
from ...utilities import trModuleWrapper
from ...pytorch import FeedForwardNetwork
from ... import NWModule
from ...serializer import NWModuleSerializer
from ...callbacks import CallbackName
from ...metrics import Metric, MetricWrapper

# @brief Abstract class of an Edge between two nodes. More specific edge types must overwrite getModel().
# @param[in] inputNode Instance of the input node of this edge
# @param[in] outputNode Instance of the output node of this edge
class Edge(FeedForwardNetwork, ABC):
	def __init__(self, inputNode:Node, outputNode:Node, name:Optional[str]=None, hyperParameters:Dict={}):
		FeedForwardNetwork.__init__(self, hyperParameters=hyperParameters)
		name = "%s -> %s" % (str(inputNode), str(outputNode)) if name is None else name
		self.name = name
		self.inputNode = inputNode
		self.outputNode = outputNode
		self.model = self.getModel()
	
	@abstractmethod
	def getModel(self) -> NWModule:
		pass

	@abstractmethod
	def getCriterion(self) -> Callable:
		pass

	def getNodes(self) -> Tuple[Node, Node]:
		return [self.inputNode, self.outputNode]

	def forward(self, x):
		return self.model.forward(x)

	def __str__(self):
		return self.name

	def __repr__(self):
		return str(self)