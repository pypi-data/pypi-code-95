import numpy as np

def AssignToRecarray(a,b,i0=0,i1=None):
	
	adt = a.dtype.names
	bdt = b.dtype.names
	
	n = np.size(adt)
	for i in range(0,n):
		if adt[i] in bdt:
			b[adt[i]][i0:i1] = a[adt[i]]

	return b
