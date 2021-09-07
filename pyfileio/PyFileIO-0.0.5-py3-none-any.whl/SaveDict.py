from .SaveObject import SaveObject

def SaveDict(Obj,Fname):
	'''
	This function saves the contents of a python object into a 
	binary file using pickle.
	
	Inputs:
		Obj: python object
		Fname: path to output file.
	
	'''
	print('Depreciation warning: SaveDict will be removed in the next version, use SaveObject instead')	
	SaveObject(Obj,Fname)
	
