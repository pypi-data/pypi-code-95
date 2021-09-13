import numpy as np
import pickle
from typing import Any
from .debug import Debug

def isPicklable(item):
	try:
		_ = pickle.dumps(item)
		return True
	except Exception as e:
		Debug.print("Item is not pickable: %s" % (e))
		return False

def getFormattedStr(item:Any, precision:int) -> str: # type: ignore
	formatStr = "%%2.%df" % (precision)
	if isinstance(item, (list, tuple, set, np.ndarray)): # type: ignore
		return [getFormattedStr(x, precision) for x in item] # type: ignore
	elif isinstance(item, dict): # type: ignore
		return {k:getFormattedStr(v, precision) for k, v in item.items()} # type: ignore
	else:
		return formatStr % (item) # type: ignore
