import numpy as np

def ReadASCIIFile(fname):
	'''
	This function will simply read an ASCII file into a numpy array.
	
	Input:
		fname: path to file
		
	Return:
		numpy.ndarray of strings
	'''
	f = open(fname,'r')
	data = f.readlines()
	f.close()
	data = np.array(data)
	return data
