import numpy as np
from typing import Union
from collections import OrderedDict

# Deep check if two items are equal. Dicts are checked value by value and numpy array are compared using "closeEnough"
#  method
def deepCheckEqual(a, b):
	assert type(a) == type(b), "Types %s and %s differ." % (type(a), type(b))

	Type = type(a)
	if isinstance(a, (dict, OrderedDict)):
		for key in a:
			if not deepCheckEqual(a[key], b[key]):
				return False
		return True
	elif isinstance(a, (np.ndarray, list, tuple)):
		if not len(a) == len(b):
			return False
		for i in range(len(a)):
			if not deepCheckEqual(a[i], b[i]):
				return False
		return True
	return a == b

def deepPrettyPrint(d, depth=0):
	dphStr = " "  * depth
	if isinstance(d, dict):
		print("\n%sDict {" % dphStr, end="")
		for k in d:
			print("\n%s- %s:" % (dphStr, k), end="")
			deepPrettyPrint(d[k], depth+1)
			print("")
		print("%s}" % dphStr)
	elif isinstance(d, (tuple, list)):
		Len = len(d)
		print("\n%sList (%d) [" % (dphStr, Len), end="")
		for i in range(len(d)):
			print("")
			deepPrettyPrint(d[i], depth+1)
		print("%s]" % dphStr)
	elif isinstance(d, np.ndarray):
		print("\n%sArray (%s) [" % (dphStr, npGetInfo(d)), end="")
		for i in range(len(d)):
			deepPrettyPrint(d[i], depth+1)
		print("%s]" % dphStr)
	else:
		print("%s" % d, end="")
	# else:
	# 	print("%s- %s. Type: %s"% (dphStr, k, type(d[k])))
