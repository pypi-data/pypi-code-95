import numpy as np

def JoinRecarray(a0,a1):
	'''
	Simple routine to append two numpy.recarrays.
	
	Inputs
	======
	a0 : numpy.recarray
		First recarray object.
	a1 : numpy.recarray
		Second recarray object (must have same dtypes as a1!).
		
	Returns
	=======
	out : numpy.recarray 
		New numpy.recarray with data from a0 at the beginning and a1 at
		the end.
	'''
	dt = a1.dtype
	n0 = np.size(a0)
	n1 = np.size(a1)
	
	out = np.recarray(n0+n1,dtype=dt)
	out[0:n0] = a0
	out[n0:n0+n1] = a1
	
	return out
