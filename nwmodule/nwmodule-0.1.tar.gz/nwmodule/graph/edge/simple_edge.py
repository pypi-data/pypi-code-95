import torch.nn as nn
from overrides import overrides
from typing import Callable
from .edge import Edge
from ... import NWModule
from ...utilities import trModuleWrapper

class SimpleEdge(Edge):
	@overrides
	def getModel(self) -> NWModule:
		if hasattr(self, "model"):
			print("[Simple Edge] Model already instantiated, returning early.")
			return self.model
		A, B = self.inputNode, self.outputNode
		encoder = A.getEncoder(B)
		decoder = B.getDecoder(A)
		model = trModuleWrapper(nn.Sequential(encoder, decoder))
		self.addMetrics(B.getNodeMetrics())
		return model

	@overrides
	def getCriterion(self) -> Callable:
		return self.outputNode.getNodeCriterion()
