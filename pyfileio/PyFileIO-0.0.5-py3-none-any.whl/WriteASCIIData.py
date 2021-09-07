import numpy as np
from .WriteASCIIFile import WriteASCIIFile

def WriteASCIIData(fname,data,SplitChar=' '):
	
	#create empty string array
	n = data.size
	lines = np.zeros(n+1,dtype='object')
	names = data.dtype.names
	nc = len(names)
	cols = np.zeros((n,nc),dtype='object')
	
	#create header
	head = SplitChar.join(names) + '\n'
	lines[0] = head
	
	#format each string
	for i in range(0,nc):
		cols[:,i] = data[names[i]].astype('U')
		
	#combine strings
	for i in range(0,n):
		lines[i+1] = SplitChar.join(cols[i]) + '\n'
		
	#save file
	WriteASCIIFile(fname,lines)
	
