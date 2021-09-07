import numpy as np
from .ProgressBar import ProgressBar
import os

def ReadRecarray(Fname,dtype,Progress=False):
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
		
	Returns
	=======
	data : numpy.recarray object
	
	'''
	#obtain file size
	tbytes = (os.stat(Fname).st_size)
	
	#open the file and count the number of records
	f = open(Fname,'rb')
	N = np.fromfile(f,dtype='int32',count=1)

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
			shape = (Ne[0],)
		else:
			s = dtype[i][2] 
			Ns = len(s)
			Ne = np.array(N)
			shape = (N[0],)
			for j in range(0,Ns):
				Ne *= s[j]
				shape += (s[j],)
				
		#read the required number of elements from the file and reshape if needed
		if len(shape) == 1:
			data[dtype[i][0]] = np.fromfile(f,dtype=dtype[i][1],count=Ne[0])
		else:
			tmp = np.fromfile(f,dtype=dtype[i][1],count=Ne[0])	
			data[dtype[i][0]] = tmp.reshape(shape)
		if Progress:
			nbytes += data[dtype[i][0]].nbytes
			pb.Display(nbytes)
	f.close()
	return data
	
