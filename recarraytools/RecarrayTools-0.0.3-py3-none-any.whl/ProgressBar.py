import numpy as np

units = [(1.0,'B'),(1024.0,'kiB'),(1024.0**2,'MiB'),(1024.0**3,'GiB'),
		(1024.0**4,'TiB'),(1024.0**5,'PiB')]


class ProgressBar(object):
	def __init__(self,nbytes,barlen=50):
		'''
		Progress bar for loading and saving data.
		
		Inputs
		======
		nbytes : integer or float
			Total number of bytes being read/written
		barlen : integer
			Length of bar
		'''
		
		self.nbytes = nbytes
		self.barlen = barlen
		order = np.log10(nbytes)
		ind = np.min([np.int32(order/3.0),5])
		self.mult,self.units = units[ind]
		self.mult = 1.0/self.mult
		
	def Display(self,b):
		'''
		Display the progress bar at some level of progress.
		
		Inputs
		======
		b	:	integer or float
			number of bytes
		
		'''
		frac = b/self.nbytes
		perc = 100.0*frac
		nhash = np.int32(np.round(self.barlen*frac))
		ndash = self.barlen - nhash
		bar = '['+'#'*nhash+'-'*ndash+']'
		if self.units == 'B':
			bstr = ' {:4d}/{:4d} '.format(np.int32(b),np.int32(self.nbytes))+self.units
		else:
			bstr = ' {:6.1f}/{:6.1f} '.format(np.float32(self.mult*b),np.float32(self.mult*self.nbytes))+self.units
		pstr = ' ({:6.2f}%)'.format(perc)
		print('\r'+bar+bstr+pstr,end='')
		
	def __del__(self):	
		print('\nDone')
