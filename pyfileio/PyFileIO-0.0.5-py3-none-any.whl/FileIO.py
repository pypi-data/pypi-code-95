import numpy as np

def ArrayToFile(x,dtype,f):
	'''
	Saves numpy.ndarray to file
	
	Inputs:
		x: numpy.ndarray to be saved
		dtype: numpy dtype to use for saving
		f: open file object (make sure to open with 'wb' option)
		
	'''
	n = np.size(x)
	np.int32(n).tofile(f)
	_x = np.array(x).astype(dtype)
	ns = np.int32(np.size(_x.shape))
	sh = np.array(_x.shape).astype('int32')
	ns.tofile(f)
	sh.tofile(f)
	_x.tofile(f)
		
def ArrayFromFile(dtype,f):
	'''
	Reads numpy.ndarray from file
	
	Inputs:
		dtype: numpy dtype of saved array
		f: open file object (make sure to open with 'rb' option)
		
	Returns:
		numpy.ndarray
		
	'''
	n = np.fromfile(f,dtype='int32',count=1)
	if np.size(n) == 0:
		return None
	else:
		n = n[0]
	ns = np.fromfile(f,dtype='int32',count=1)[0]
	sh = np.fromfile(f,dtype='int32',count=ns)
	x = np.fromfile(f,dtype=dtype,count=n).reshape(tuple(sh))
	return x
	
def ScalarToFile(x,dtype,f):
	'''
	Saves scalar variable to file
	
	Inputs:
		x: scalar to be saved
		dtype: numpy dtype to use for saving
		f: open file object (make sure to open with 'wb' option)
		
	'''
	np.array(x).astype(dtype).tofile(f)

def ScalarFromFile(dtype,f):
	'''
	Reads a scalar variable from file
	
	Inputs:
		dtype: numpy dtype of saved scalar
		f: open file object (make sure to open with 'rb' option)
		
	Returns:
		scalar value
		
	'''
	x = np.fromfile(f,dtype=dtype,count=1)
	if np.size(x) == 0:
		return None
	else:
		x = x[0]
	return x
		
def StringsToFile(x,f):
	'''
	Saves list or aray of strings to file
	
	Inputs:
		x: strings to be saved
		f: open file object (make sure to open with 'wb' option)
		
	'''
	n = np.size(x)
	np.int32(n).tofile(f)
	_x = np.array(x).astype('U')
	if n > 1:
		l = np.int32(str(_x.dtype)[2:])
	else:
		l = np.int32(len(x))
	l.tofile(f)
	_x.tofile(f)
		
def StringsFromFile(f):
	'''
	Reads lsit or array of strings from file
	
	Inputs:
		f: open file object (make sure to open with 'rb' option)
		
	Returns:
		numpy.ndarray of strings
		
	'''
	n = np.fromfile(f,dtype='int32',count=1)
	if np.size(n) == 0:
		return None
	else:
		n = n[0]
	l = np.fromfile(f,dtype='int32',count=1)[0]
	x = np.fromfile(f,dtype='U{:d}'.format(l),count=n)
	if n == 1:
		return x[0]
	else:
		return x
		
def ListArrayToFile(x,dtype,f):
	'''
	Saves list of numpy.ndarrays to file
	
	Inputs:
		x: list to be saved
		dtype: numpy dtype to use for saving
		f: open file object (make sure to open with 'wb' option)
		
	'''
	l = np.int32(len(x))	
	l.tofile(f)
	for i in range(0,l):
		ArrayToFile(x[i],dtype,f)
		
def ListArrayFromFile(dtype,f):
	'''
	Reads list of numpy.ndarrays from file
	
	Inputs:
		dtype: numpy dtype of saved arrays
		f: open file object (make sure to open with 'rb' option)
		
	Returns:
		list of numpy.ndarrays
		
	'''
	l = np.fromfile(f,dtype='int32',count=1)
	if np.size(l) == 0:
		return None
	else:
		l = l[0]
	x = []
	for i in range(0,l):
		x.append(ArrayFromFile(dtype,f))
	return x
