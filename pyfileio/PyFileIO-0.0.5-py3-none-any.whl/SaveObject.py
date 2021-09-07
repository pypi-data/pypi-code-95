import pickle

def SaveObject(Obj,Fname):
	'''
	This function saves the contents of a python object into a 
	binary file using pickle.
	
	Inputs:
		Obj: python object
		Fname: path to output file.
	
	'''
	f = open(Fname,'wb')
	pickle.dump(Obj,f,pickle.HIGHEST_PROTOCOL)
	f.close()
	
