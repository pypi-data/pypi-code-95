import os
import pickle

def LoadObject(Fname):
	'''
	Loads a python object from a file.
	
	Inputs:
		Fname: file name and path.
		
	Output:
		python object.
	'''
	if not os.path.isfile(Fname):
		print('File not found')
		return None
	
	try:
		f = open(Fname,'rb')
		Obj = pickle.load(f)
		f.close()
	except:
		f = open(Fname,'rb')
		Obj = pickle.load(f,encoding='latin1')
		f.close()		
	return Obj
