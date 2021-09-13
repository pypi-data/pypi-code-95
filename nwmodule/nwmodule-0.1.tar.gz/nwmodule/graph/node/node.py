from __future__ import annotations
import torch as tr
import torch.nn as nn
from typing import Optional, Dict, Type, Union, Callable, Any, Tuple
from abc import ABC, abstractmethod
from overrides import overrides
from ...nwmodule import NWModule
from ...utilities import trGetData, trDetachData
from ...metrics import Metric
from ..message import Message

GTType = Optional[Union[Dict[Any, Any], tr.Tensor]]
CriterionType = Callable[[tr.Tensor, tr.Tensor, dict], tr.Tensor]

class Node(ABC, nn.Module):
	# A dictionary that gives a unique tag to all nodes by appending an increasing number to name.
	lastNodeID = 0
	names = set()

	def __init__(self, name:str, hyperParameters:dict={}):
		super().__init__()
		self.name = name

		# Set up hyperparameters for this node (used for saving/loading identical node)
		self.hyperParameters = self.getHyperParameters(hyperParameters)
		# Messages are the items received at this node via all its incoming edges.
		self.messages:List[Message] = set()

	@abstractmethod
	def getEncoder(self, outputNode:Optional[Node]=None) -> NWModule:
		pass

	@abstractmethod
	def getDecoder(self, inputNode:Optional[Node]=None) -> NWModule:
		pass

	@abstractmethod
	def getNodeMetrics(self) -> Dict[str, Metric]:
		pass

	@abstractmethod
	def getNodeCriterion(self) -> CriterionType:
		pass

	# @brief A method that converts the existing messages of the current steps into a new representation
	# Can be seen as messages = f(messages).
	@abstractmethod
	def aggregate(self):
		pass

	def clearMessages(self):
		self.messages = set()

	def addMessage(self, message:Message):
		assert isinstance(message, Message)
		self.messages.add(message)

	def getMessages(self) -> List[Message]:
		return self.messages

	def getHyperParameters(self, hyperParameters:dict) -> dict:
		# This is some weird bug. If i leave the same hyperparameters coming (here I make a shallow copy),
		#  making two instances of the same class results in having same hyperparameters.
		hyperParameters = {k : hyperParameters[k] for k in hyperParameters.keys()}
		hyperParameters["name"] = self.name
		return hyperParameters

	def __str__(self) -> str:
		return self.name

	def __repr__(self) -> str:
		return self.name

	# This and __eq__ are used so we can put node in dict and access them via strings
	def __hash__(self):
		return hash(self.name)
	
	def __eq__(self, x) -> bool:
		if isinstance(x, Node):
			x = x.name
		return self.name == x
