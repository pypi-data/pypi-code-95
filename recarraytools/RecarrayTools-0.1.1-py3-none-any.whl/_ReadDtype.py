import numpy as np

def _ReadDtype(f):
	'''
	Attempt to read the dtype of the file, if it fails None will be 
	returned.
	
	'''
	
	#seek the beginning of the file
	f.seek(0,0)
	
	#read the zero integer at the start
	n = np.fromfile(f,dtype='uint32',count=1)[0]
	if n != 0:
		#this means that there isn't a dtype stored in the file,
		#instead it is the number of records
		return n
	
	#read the version string
	lv = np.fromfile(f,dtype='uint32',count=1)[0]
	ver = str(np.fromfile(f,dtype='<U{:d}'.format(lv),count=1)[0])

	
	#read the number of dtypes
	ndt = np.fromfile(f,dtype='uint32',count=1)[0]
	#and the codes
	end = np.fromfile(f,dtype='U1',count=ndt)
	dtc = np.fromfile(f,dtype='U1',count=ndt)
	dln = np.fromfile(f,dtype='uint16',count=ndt)

	#read the shape
	dsh = np.zeros(ndt,dtype='O')
	for i in range(0,ndt):
		nsh = np.fromfile(f,dtype='int32',count=1)[0]
		if nsh == 0:
			dsh[i] = None
		else:
			sh = tuple(np.fromfile(f,dtype='int32',count=nsh))
			dsh[i] = sh
			
	#read the names
	dnm = np.zeros(ndt,dtype='O')
	for i in range(0,ndt):
		ld = np.fromfile(f,dtype='uint32',count=1)[0]
		dnm[i] = str(np.fromfile(f,dtype='<U{:d}'.format(ld),count=1)[0])
	
	#convert this into a dtype list
	dtype = []
	for i in range(0,ndt):
		if dtc[i] == 'O':
			dt = 'O'
		else:
			if dln[i] > 0:
				dt = '{:s}{:d}'.format(dtc[i],dln[i])
			else:
				dt = '{:s}'.format(dtc[i],dln[i])
			if end[i] in ['<','>']:
				dt = '{:s}'.format(end[i]) + dt
		if dsh[i] is None:
			dtype.append((dnm[i],dt))
		else:
			dtype.append((dnm[i],dt,dsh[i]))

	return dtype
