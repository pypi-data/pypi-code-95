from overrides import overrides
from typing import List, Dict
from ..serializer import NWModuleSerializer, getTrainableParameters, _computeNumParams
from ..utilities import Debug

class GraphSerializer(NWModuleSerializer):
	@overrides
	def doSerialization(self, stateKeys:List[str]) -> Dict:
		result = {}
		for edge in self.model.edges:
			if edge.getNumParams()[0] > 0:
				result[edge.name] = edge.serializer.doSerialization(stateKeys)
		# Store graph level history dict/callbacks and model state in the key "None"
		result[None] = super().doSerialization(["history_dict", "callbacks", "model_state"])
		return result

	@overrides
	def loadModel(self, path, stateKeys):
		pklFile = NWModuleSerializer.readPkl(path)
		for edge in self.model.edges:
			Debug.log(3, "Loading edge '%s'" % edge)
			if not edge.name in pklFile:
				Debug.log(2, \
					"[GraphSerializer::loadModel] Edge '%s' has no model state to be loaded. Skipping." % edge)
				continue
			edgeState = pklFile[edge.name]
			edge.serializer.doLoadModel(edgeState, stateKeys)
		# Load graph level state
		super().doLoadModel(pklFile[None], ["history_dict", "callbacks", "model_state"])