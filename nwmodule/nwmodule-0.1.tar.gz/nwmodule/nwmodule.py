import sys
import torch as tr
import torch.nn as nn
import torch.optim as optim
import numpy as np
from datetime import datetime
from copy import deepcopy
from collections import OrderedDict
from collections.abc import Iterable
from typing import List, Union, Dict, Callable, Optional, Generator
from types import LambdaType
from nwdata.utils import RunningMean, deepCheckEqual, topologicalSort

from abc import abstractmethod, ABC
from .serializer import NWModuleSerializer
from .utilities import isBaseOf, getFormattedStr, Debug, getNumParams, npGetData, trGetData
from .utilities.tr_utils import _getOptimizerStr
from .callbacks import Callback, CallbackName
from .metrics import Metric, MetricWrapper

np.set_printoptions(precision=3, suppress=True)
CriterionType = Callable[[tr.Tensor, tr.Tensor], tr.Tensor]

# Wrapper on top of the PyTorch model. Added methods for saving and loading a state. To completly implement a PyTorch
#  model, one must define layers in the object's constructor, call setOptimizer, setCriterion and implement the
#  forward method identically like a normal PyTorch model.
class NWModule(nn.Module, ABC):
	def __init__(self, hyperParameters:Optional[Dict]=None):
		super().__init__()
		self.optimizer:Optional[optim.Optim] = None
		self.optimizerScheduler = None
		self.serializer = NWModuleSerializer(self)
		self.reset_parameters()
		self.hyperParameters = {}
		self.setHyperParameters(hyperParameters)

	# The network algorithm. This must be updated for specific networks, so the whole metric/callbacks system works
	#  just as before.
	# @param[in] trInputs The inputs of the network
	# @param[in] trLabels The labels of the network
	# @return The results of the network and the loss as given by the criterion function
	@abstractmethod
	def networkAlgorithm(self, trInputs, trLabels, isTraining:bool=False, isOptimizing:bool=False):
		pass

	##### Metrics, callbacks and hyperparameters #####

	# @brief Adds hyperparameters to the dictionary. Only works if the model has not been trained yet (so we don't)
	#  update the hyperparameters post-training as it would invalidate the whole principle.
	def setHyperParameters(self, hyperParameters:Dict):
		assert self.hyperParameters == {}, \
			"Clear the existing hyperparameters before setting them. Current: %s. New: %s" % \
			(self.hyperParameters, hyperParameters)
		hyperParameters = hyperParameters if not hyperParameters is None else {}
		assert isinstance(hyperParameters, dict)
		self.hyperParameters = hyperParameters

	def invalidateTopologicalSort(self):
		# See warning for add Metrics
		self.topologicalSort = np.arange(len(self.callbacks))
		self.topologicalKeys = np.array(list(self.callbacks.keys()))[self.topologicalSort]
		self.topologicalSortDirty = True

	def addMetric(self, metricName:Union[str, CallbackName], metric:Union[Callable, Metric]):
		# partial or lambda but not metric
		if isinstance(metric, (Callable, LambdaType, Callback)) and (not isinstance(metric, Metric)): #type: ignore
			metric = MetricWrapper(metric) #type: ignore
		if not isinstance(metricName, CallbackName): #type: ignore
			metricName = CallbackName(metricName) #type: ignore
		if metricName in self.callbacks:
			raise Exception("Metric %s already exists" % (metricName))

		metric.setName(metricName) #type: ignore
		self.callbacks[metricName] = metric
		self.invalidateTopologicalSort()

	# Sets the user provided list of metrics as callbacks and adds them to the callbacks list.
	def addMetrics(self, metrics:Dict[str, Union[Callable, Metric]]):
		assert isinstance(metrics, dict), "Metrics must be provided as Str=>Callback dictionary"

		for metricName, metric in metrics.items():
			if metricName == "Loss":
				continue
			assert metricName not in self.callbacks, "Metric %s already in callbacks list." % (metricName)
			self.addMetric(metricName, metric)
		# Warning, calling addMetrics will invalidate topological sort as we reset the indexes here. If there are
		#  dependencies already set using setCallbacksDependeices, it must be called again.
		self.invalidateTopologicalSort()

	def addCallback(self, callback:Callback):
		assert isBaseOf(callback, Callback), \
			"Expected only subclass of types Callback, got type %s" % (type(callback))
		assert callback.name not in self.callbacks, "Callback %s already in callbacks list." % (callback.name)
		self.callbacks[callback.name] = callback
		# Warning, calling addCallbacks will invalidate topological sort as we reset the indexes here. If there are
		#  dependencies already set using setCallbacksDependeices, it must be called again.
		# TODO: see if this is needed or we can add a new node to the existing topological sort graph
		self.invalidateTopologicalSort()

	# Adds the user provided list of callbacks to the model's list of callbacks (and metrics)
	def addCallbacks(self, callbacks:List[Callback]):
		for callback in callbacks:
			self.addCallback(callback)

	# TODO: Add clearMetrics. Store dependencies, so we can call topological sort before/after clearCallbacks.
	# Store dependencies on model store. Make clearCallbacks clear only callbacks, not metrics as well.
	def clearMetrics(self):
		metrics = [x.name for x in filter(lambda x : isBaseOf(x, Metric), self.callbacks.values())]
		newCallbacks = OrderedDict({})
		for key in self.callbacks:
			callback = self.callbacks[key]
			if not isBaseOf(callback, Metric):
				newCallbacks[key] = callback
		self.callbacks = newCallbacks
		self.invalidateTopologicalSort()

	def clearCallbacks(self):
		self.callbacks = OrderedDict()
		self.addMetric("Loss", lambda y, t, **k : k["loss"])
		self.invalidateTopologicalSort()

	# Does a topological sort on the given list of callback dependencies. This MUST be called after all addMetrics and
	#  addCallbacks are called, as these functions invalidate the topological sort.
	def setCallbacksDependencies(self, dependencies):
		# Convert strings and callbacks to CallbackNames
		convertedDependencies = {}
		for key in dependencies:
			items = dependencies[key]
			if isinstance(key, str):
				key = CallbackName(key)
			if isBaseOf(key, Callback):
				key = key.getName()
			convertedDependencies[key] = []
			for item in items:
				if isinstance(item, str):
					item = CallbackName(item)
				if isBaseOf(item, Callback):
					item = item.getName()
				convertedDependencies[key].append(item)

		for key in convertedDependencies:
			items = convertedDependencies[key]

			if not key in self.callbacks:
				assert False, "Key %s is not in callbacks (%s)" % (key, list(self.callbacks.keys()))

			for depKey in items:
				if not depKey in self.callbacks:
					assert False, "Key %s of dependency %s is not in callbacks (%s)" \
						% (depKey, key, list(self.callbacks.keys()))

		for key in self.callbacks:
			assert isinstance(key, CallbackName)
			if not key in convertedDependencies:
				convertedDependencies[key] = []

		order = topologicalSort(convertedDependencies)
		callbacksKeys = list(self.callbacks.keys())
		self.topologicalSort = np.array([callbacksKeys.index(x) for x in order])
		self.topologicalKeys = np.array(list(self.callbacks.keys()))[self.topologicalSort]
		Debug.log(2, "Successfully done topological sort!")


	##### Training / testing functions

	def updateOptimizer(self, trLoss, isTraining:bool, isOptimizing:bool, retain_graph=False):
		if not trLoss is None:
			if isTraining and isOptimizing:
				assert not self.getOptimizer() is None, "Set optimizer when training"
				self.getOptimizer().zero_grad()
				trLoss.backward(retain_graph=retain_graph)
				self.getOptimizer().step()
			else:
				trLoss.detach_()

	def trainGeneratorNumSteps(self, generator:Generator, numSteps:int, numEpochs:int, \
		validationGenerator:Optional[Generator]=None, validationNumSteps:int=0):
		from .nwtrainer import NWTrainer
		return NWTrainer(self).train(generator, numSteps, numEpochs, validationGenerator, validationNumSteps)

	# @param[in] generator Generator which is used to get items for numEpochs epochs, each taking len(generator) steps
	# @param[in] numEpochs The number of epochs the network is trained for
	# @param[in] validationGenerator Validation Generator used to validate the results. If not provided, generator
	#  parameter is used as validation as well for various callbacks (i.e. SaveModels)
	def trainGenerator(self, generator:Generator, numEpochs:int, validationGenerator:Optional[Generator]=None):
		validationNumSteps = 0 if validationGenerator is None else len(validationGenerator)
		self.trainGeneratorNumSteps(generator, len(generator), numEpochs, validationGenerator, validationNumSteps)

	def testGeneratorNumSteps(self, generator:Generator, numSteps):
		from .nwtrainer import NWTrainer
		return NWTrainer(self).test(generator, numSteps)

	# @brief Tests the model given a generator
	# @param[in] The generator used to yield testing data
	def testGenerator(self, generator:Generator):
		return self.testGeneratorNumSteps(generator, len(generator))

	def metricsSummary(self) -> str:
		metrics = self.getMetrics().values()
		summaryStr = ""
		for metric in metrics:
			summaryStr += "\t- %s (%s)\n" % (metric.getName(), metric.getDirection())
		return summaryStr

	def callbacksSummary(self) -> str:
		callbackNames = " | ".join(list(map(lambda x : str(x.getName()), self.getCallbacks())))
		return callbackNames

	def getNumParams(self):
		return getNumParams(self)

	def summary(self) -> str:
		summaryStr = "[Model summary]\n"
		summaryStr += self.__str__() + "\n"

		numParams, numTrainable = self.getNumParams()
		summaryStr += "Parameters count: %d. Trainable parameters: %d.\n" % (numParams, numTrainable)

		summaryStr += "Hyperparameters:\n"
		for hyperParameter in self.hyperParameters:
			summaryStr += "\t- %s: %s\n" % (hyperParameter, self.hyperParameters[hyperParameter])

		summaryStr += "Metrics:\n"
		summaryStr += self.metricsSummary()

		summaryStr += "Callbacks:\n"
		summaryStr += "\t%s\n" % (self.callbacksSummary())

		summaryStr += "Optimizer: %s\n" % self.getOptimizerStr()
		summaryStr += "Optimizer Scheduler: %s\n" % ("None" if not self.optimizerScheduler \
			else str(self.optimizerScheduler))

		summaryStr += "GPU: %s" % (tr.cuda.is_available())

		return summaryStr

	def __str__(self):
		return "General neural network architecture. Update __str__ in your model for more details when using summary."

	##### Misc functions #####

	# Useful to passing numpy data but still returning backpropagable results
	def npForwardTrResult(self, *args, **kwargs):
		device = next(self.parameters()).device
		trArgs = trGetData(args, device)
		trKwargs = trGetData(kwargs, device)
		trResult = self.forward(*trArgs, **trKwargs)
		return trResult

	# Wrapper for passing numpy arrays, converting them to torch arrays, forward network and convert back to numpy
	# @param[in] x The input, which can be a numpy array, or a list/tuple/dict of numpy arrays
	# @return y The output of the network as numpy array
	def npForward(self, *args, **kwargs):
		with tr.no_grad():
			trResult = self.npForwardTrResult(*args, **kwargs)
		npResult = npGetData(trResult)
		return npResult

	def saveWeights(self, path):
		return self.serializer.saveModel(path, stateKeys=["weights", "model_state"])

	def loadWeights(self, path, yolo=False):
		Debug.log(1, "[NWModule::loadWeights] Loading weights from %s" % path)
		if yolo:
			loadedState = NWModuleSerializer.readPkl(path)
			assert "weights" in loadedState
			Debug.log(2, "[NWModule::loadWeights] YOLO mode. No state & named params check.")
			self.serializer.doLoadWeights(loadedState["weights"], allowNamedMismatch=True)
		else:
			self.serializer.loadModel(path, stateKeys=["model_state", "weights"])

	def saveModel(self, path):
		return self.serializer.saveModel(path, stateKeys=["weights", "optimizer", \
			"history_dict", "callbacks", "model_state"])

	def loadModel(self, path):
		self.serializer.loadModel(path, stateKeys=["weights", "optimizer", "history_dict", "callbacks", "model_state"])

	def onModelSave(self):
		return self.hyperParameters

	def onModelLoad(self, state):
		# if len(self.hyperParameters.keys()) != len(state.keys()):
		# 	return False

		allKeys = set(list(self.hyperParameters.keys()) + list(state.keys()))
		for key in allKeys:
			if not key in self.hyperParameters:
				return False

			if not key in state:
				Debug.log(2, "Warning. Model has unknown state key: %s=%s, possibly added after training. Skipping." \
					% (key, str(self.hyperParameters[key])))
				continue
			loadedState = state[key]
			modelState = self.hyperParameters[key]

			if not deepCheckEqual(loadedState, modelState):
				return False
		return True
	
	def isTrainable(self):
		for param in self.parameters():
			if param.requires_grad == True:
				return True
		return False

	def reset_parameters(self):
		# Setup print message keys, callbacks & topological sort variables
		self.clearCallbacks()

		# A list that stores various information about the model at each epoch. The index in the list represents the
		#  epoch value. Each value of the list is a dictionary that holds by default only loss value, but callbacks
		#  can add more items to this (like confusion matrix or accuracy, see mnist example).
		self.trainHistory = []

		for layer in self.children():
			if isinstance(layer, Iterable):
				for i in range(len(layer)):
					if not hasattr(layer[i], "reset_parameters"):
						Debug.log(2, "[NWModule::reset_parameters] Sublayer '%s' has no reset_parameters() method" % \
							layer[i])
						continue
					layer[i].reset_parameters()
			else:
				if not hasattr(layer, "reset_parameters"):
					Debug.log(2, "[NWModule::reset_parameters] Sublayer '%s' has no reset_parameters() method" % \
						layer)
					continue
				layer.reset_parameters()

	### Getters and setters

	# Returns only the callbacks that are of subclass Callback (not metrics)
	def getCallbacks(self):
		res = list(filter(lambda x : not isBaseOf(x, Metric), self.callbacks.values()))
		return res

	def getMetrics(self):
		metrics = {}
		for k, v in self.callbacks.items():
			if isinstance(v, Metric):
				metrics[k] = v
		return metrics

	def getMetric(self, metricName) -> Metric:
		for key, callback in self.callbacks.items():
			if not isBaseOf(callback, Metric):
				continue
			if callback.name == metricName:
				return callback
		assert False, "Metric %s was not found. Use adddMetrics() properly first." % metricName

	def getTrainHistory(self):
		return self.trainHistory

	def setTrainableWeights(self, value):
		for param in self.parameters():
		    param.requires_grad = value

	# Optimizer can be either a class or an object. If it's a class, it will be instantiated on all the trainable
	#  parameters, and using the arguments in the variable kwargs. If it's an object, we will just use that object,
	#  and assume it's correct (for example if we want only some parameters to be trained this has to be used)
	# Examples of usage: model.setOptimizer(nn.Adam, lr=0.01), model.setOptimizer(nn.Adam(model.parameters(), lr=0.01))
	def setOptimizer(self, optimizer, **kwargs):
		if isinstance(optimizer, optim.Optimizer):
			self.optimizer = optimizer
		else:
			trainableParams = list(filter(lambda p : p.requires_grad, self.parameters()))
			assert len(trainableParams) > 0, "Optimizer must have some trainable parameters."
			self.optimizer = optimizer(trainableParams, **kwargs)
		self.optimizer.storedArgs = kwargs

	def getOptimizer(self):
		return self.optimizer

	def getOptimizerStr(self):
		optimizer = self.getOptimizer()
		return _getOptimizerStr(optimizer)

	def setOptimizerScheduler(self, scheduler, **kwargs):
		assert not self.getOptimizer() is None, "Optimizer must be set before scheduler!"
		if isinstance(scheduler, optim.lr_scheduler._LRScheduler):
			self.optimizerScheduler = scheduler
		else:
			self.optimizerScheduler = scheduler(optimizer=self.getOptimizer(), **kwargs)
			# Some schedulers need acces to the model's object. Others, will not have this argument.
			self.optimizerScheduler.model = self
			self.optimizerScheduler.storedArgs = kwargs

	def setCriterion(self, criterion:CriterionType):
		# If getCriterion fails, then no other criterion was set. However, if it's okay (either via other setCriterion
		#  or via overriding the mothod in another class), then shout a debug log since this may be a logic bug.
		try:
			_ = self.getCriterion()
			Debug.log(2, "[NWModule::setCriterion] Overwriting an existing criterion!")
		except Exception:
			pass
		self.criterion = criterion

	def getCriterion(self) -> CriterionType:
		if not hasattr(self, "criterion"):
			assert False, "Must be implemented"
		assert isinstance(self.criterion, Callable)
		return self.criterion