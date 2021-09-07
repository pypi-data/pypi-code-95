import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.interpolate import interp1d

def _InterpGaps(x,y,newx,Spline=True):
	'''
	This function will look for gaps in data and try to interpolate 
	between them onto a new x-axis, preserving the orignal gaps.
	
	Inputs
	======
	x : float
		Monotonically increasing array (e.g. time).
	y : float
		Array of data corresponding to x, where bad data are marked with 
		NaN.
	newx : float
		New x array to interpolate onto where possible.
	Spline : bool
		Boolean to try and use splint interpolation where possible.
			
	Returns
	=======
	newy : float
		New interpolated data product to match newx, preserving any gaps 
		in original data.
	
	'''
	
	
	nx = np.size(x)
	finy = np.isfinite(y)
	
	newy = np.zeros(np.size(newx),dtype='float64')
	newy.fill(np.nan)
	
	st=-1
	ngd=0
	for i in range(0,nx):
		if finy[i]:
			if st == -1:
				st=i
		else:
			if st != -1:
				if ngd == 0:
					Xi0 = np.array([st])
					Xi1 = np.array([i-1])
				else:
					Xi0 = np.append(Xi0,st)
					Xi1 = np.append(Xi1,i-1)	
				st=-1
				ngd+=1
	if st != -1:
		if ngd == 0:
			Xi0 = np.array([st])
			Xi1 = np.array([nx-1])
		else:
			Xi0 = np.append(Xi0,st)
			Xi1 = np.append(Xi1,nx-1)	
		st=-1
		ngd+=1
	if ngd == 0:
		return newy 
	X0 = x[Xi0]
	X1 = x[Xi1]
	for i in range(0,ngd):
		use = np.where((x >= X0[i]) & (x <= X1[i]))[0]
		usenew = np.where((newx >= X0[i]) & (newx <= X1[i]))[0]
		if use.size > 3 and usenew.size > 0 and Spline:
			f = InterpolatedUnivariateSpline(x[use],y[use])
			newy[usenew] = f(newx[usenew])
		elif use.size > 1 and usenew.size > 0:
			f = interp1d(x[use],y[use])
			newy[usenew] = f(newx[usenew])

	return newy
