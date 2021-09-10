import numpy as np
from .ProgressBar import ProgressBar
import os
from ._ReadDtype import _ReadDtype
import pickle

#list the dtype names which will be treated as objects
objnames = ['timedelta64','Datetime64','datetime64','object','object_',
			'object0','O','Object0','M','M8']
			
def ReadRecarray(Fname,dtype=None,Progress=False,GetSize=False):
	'''
	Reads binary file into np.recarray object
	
	Inputs
	======
	Fname : str
		Full path and file name of binary file to be read.
	dtype : list
		list of data types (and optionally shapes) stored in Fname.
			e.g.:
				dtype = [('Date','int32'),('ut','float32'),('x','float64',(10,))]
	Progress : bool
		Display a progress bar.
	GetSize : bool
		if True, then only the number of records is returned.
		
	Returns
	=======
	data : numpy.recarray object
	
	'''
	#obtain file size
	tbytes = (os.stat(Fname).st_size)
	
	#open the file and count the number of records
	f = open(Fname,'rb')
	N = np.fromfile(f,dtype='int32',count=1)[0]
	if N == 0 and tbytes > 4:
		#dtype likely to be stored inside the file
		dtype = _ReadDtype(f)
		#get the number of records again
		N = np.fromfile(f,dtype='int32',count=1)[0]
	elif N != 0 and dtype is None:
		#no dtype in file and no dtype supplied
		print('No dtype in file, please set "dtype" keyword')
		return None
		

	if GetSize:
		f.close()
		return N

	#init progress bar
	if Progress:
		print('Reading file: {:s}'.format(Fname))
		pb = ProgressBar(tbytes)
		nbytes = 4
		pb.Display(4)
	
	#create output recarray
	data = np.recarray(N,dtype=dtype)
	
	#loop through each dtype
	Nd = len(dtype)
	for i in range(0,Nd):
		#calculate the shape tuple
		if len(dtype[i]) == 2:
			Ne = np.array(N)
			shape = (Ne,)
		else:
			s = dtype[i][2] 
			Ns = len(s)
			Ne = np.array(N)
			shape = (N,)
			for j in range(0,Ns):
				Ne *= s[j]
				shape += (s[j],)

		#read the required number of elements from the file and reshape if needed
		if dtype[i][1] in objnames:
			data[dtype[i][0]] = pickle.load(f)
		else:
			if len(shape) == 1:
				data[dtype[i][0]] = np.fromfile(f,dtype=dtype[i][1],count=Ne)
			else:
				tmp = np.fromfile(f,dtype=dtype[i][1],count=Ne)	
				data[dtype[i][0]] = tmp.reshape(shape)

		if Progress:
			nbytes += data[dtype[i][0]].nbytes
			pb.Display(nbytes)
	f.close()
	return data
	
