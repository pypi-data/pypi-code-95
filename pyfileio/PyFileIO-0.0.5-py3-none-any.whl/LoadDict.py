from .LoadObject import LoadObject

def LoadDict(Fname):
	'''
	Loads a python object from a file.
	
	Inputs:
		Fname: file name and path.
		
	Output:
		python object.
	'''
	print('Depreciation warning: LoadDict will be removed in the next version, use LoadObject instead')
	return LoadObject(Fname)
