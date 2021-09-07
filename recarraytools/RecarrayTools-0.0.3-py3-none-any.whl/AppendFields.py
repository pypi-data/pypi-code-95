import numpy as np

def AppendFields(indata,dtypes,newdata):
	'''
	This function will append fields containing some new data dtypes to
	a numpy.recarray object. Actually, it creates a new one and deletes
	the original, but it works. The lengths of indata and newdata must 
	be equal, otherwise strange things may happen.
	
	Inputs
	======
	indata : numpy.recarray
		Original numpy.recarray
	dtypes : list
		List of tuples with dtypes of new data to be added, e.g.
				[('a','float32'),('b','int32'),('c','bool8')]
	newdata : list|tuple
		List or tuple of new data arrays e.g. (a,b,c) or [a,b,c]
		
	Returns
	=======
	outdata : numpy.recarray
		numpy.recarray object containing both the fields of the original 
		object and the new data.
	
	'''
	
	#combine the two dtype lists, create output array
	newdtype = indata.dtype.descr + dtypes
	outdata = np.recarray(indata.size,dtype=newdtype)
	
	#get list of fields from original data and copy them to the output
	names = indata.dtype.names
	for n in names:
		outdata[n] = indata[n]
	
	#check if the newdata is a numpy.recarray
	if isinstance(newdata,np.recarray):
		#copy the fields that match from newdata to the output
		newnames = newdata.dtype.names
		outnames = outdata.dtype.names
		for n in newnames:
			if n in outnames:
				outdata[n] = newdata[n]
	else:
		#assume tuple or list of data, copy each field in order
		for i in range(0,len(newdata)):
			outdata[dtypes[i][0]] = newdata[i]
			
	return outdata
			
	
