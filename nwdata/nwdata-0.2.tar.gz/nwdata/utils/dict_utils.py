import numpy as np
from typing import Dict, Any
from .np_utils import npGetInfo

# @brief Return the value of a nested dictionary key
# @param[in] d The potentially nested dictionary
# @param[in] k The potentially nested lookup key
# @return The value of the potentially nested key
def deepDictGet(d:Dict, k:Any):
	if isinstance(k, (tuple, list)):
		if len(k) == 1:
			return d[k]
		else:
			return deepDictGet(d[k[0]], k[1 :])
	else:
		return d[k]

def prettyPrintDict(d:Dict, depth:int=0):
	dphStr = " "  * depth
	for k in d:
		if isinstance(d[k], dict):
			print("%s- %s:" % (dphStr, k))
			prettyPrintDict(d[k], depth+1)
		elif isinstance(d[k], (tuple, list)):
			Len = len(d[k])
			Type = "n/a" if Len == 0 else type(d[k][0])
			print("%s- %s: Len: %s. Type: %s" % (dphStr, k, Len, Type))
		elif isinstance(d[k], np.ndarray):
			print("%s- %s: %s" % (dphStr, k, npGetInfo(d[k])))
		else:
			print("%s- %s. Type: %s"% (dphStr, k, type(d[k])))
