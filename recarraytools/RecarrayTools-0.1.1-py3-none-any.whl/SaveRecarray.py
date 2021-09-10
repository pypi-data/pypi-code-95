import numpy as np
from .ProgressBar import ProgressBar
from ._StoreDtype import _StoreDtype
import pickle

#list the dtype names which will be treated as objects
objnames = ['timedelta64','Datetime64','datetime64','object','object_',
			'object0','O','Object0','M','M8','|O','|M','|M8']

def SaveRecarray(Arr,Fname,Progress=False,StoreDtype=False):
	'''
	Thie function will save the data from a numpy.recarray to a binary
	file.
	
	Inputs
	======
	Arr : numpy.recarray
		Data to be saved.
	Fname : str
		Full path and file name of the resulting binary file.
	Progress : bool
		Display a progress bar.
	StoreDtype : bool
		If True, then numpy.dtype will be stored in the file
	'''
	#get the size of the array in bytes
	tbytes = Arr.nbytes + 4
	
	#open the output file
	N = np.int32(Arr.size)
	f = open(Fname,'wb')
	
	#store the dtype if needed
	if StoreDtype:
		_,dtc,_,Dnames = _StoreDtype(f,Arr.dtype.descr)
	else:
		Dnames = Arr.dtype.names
		dtc = [d[1] for d in Arr.dtype.descr]
	
	N.tofile(f)
	
	#create progress bar
	if Progress:
		print('Saving file: {:s}'.format(Fname))
		pb = ProgressBar(tbytes)
		pb.Display(4)
		nbytes = 4
	
	#loop through each tag and save each to file
	Nn = np.size(Dnames)
	for i in range(0,Nn):
		if dtc[i] in objnames:
			#treat as object, use pickle
			pickle.dump(Arr[Dnames[i]],f,pickle.HIGHEST_PROTOCOL)
		else:
			Arr[Dnames[i]].tofile(f)
		
		#display progress
		if Progress:
			nbytes += Arr[Dnames[i]].nbytes
			pb.Display(nbytes)
		
	f.close()
