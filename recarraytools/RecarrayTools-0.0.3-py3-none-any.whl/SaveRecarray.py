import numpy as np
from .ProgressBar import ProgressBar

def SaveRecarray(Arr,Fname,Progress=False):
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
	'''
	#get the size of the array in bytes
	tbytes = Arr.nbytes + 4
	
	#open the output file
	N = np.int32(Arr.size)
	f = open(Fname,'wb')
	N.tofile(f)
	
	#create progress bar
	if Progress:
		print('Saving file: {:s}'.format(Fname))
		pb = ProgressBar(tbytes)
		pb.Display(4)
		nbytes = 4
	
	#loop through each tag and save each to file
	Dnames = Arr.dtype.names
	Nn = np.size(Dnames)
	for i in range(0,Nn):
		Arr[Dnames[i]].tofile(f)
		
		#display progress
		if Progress:
			nbytes += Arr[Dnames[i]].nbytes
			pb.Display(nbytes)
		
	f.close()
