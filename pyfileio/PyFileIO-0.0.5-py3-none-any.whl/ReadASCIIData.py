import numpy as np
from .ReadASCIIFile import ReadASCIIFile

def ReadASCIIData(fname,Header=True,SkipLines=0,dtype=None,SplitChar=None,
	Missing=None,FillValFloat=np.nan,FillValInt=9999999,RemoveChar=None):
	'''
	This will attempt to read a formatted ASCII file into a 
	numpy.recarray object.
	
	Inputs:
		fname: name and path of file to read, or a list of strings to be 
		treated as a file.
		Header: Tells the routine to use the first line (after skipping)
			to get the column names
		SkipLines: Tels the routine to skip the first few lines before
			reading the data
		dtype:	If None then an attempt will be made to automatically 
			determine the dtype of each column, otherwise set to a list
			of tuples containing the dtype and column names e.g.
			[('a','float32'),('b','int32')]
		SplitChar: By default the character separating the fields is
			space or tab, set this variable to a string with the 
			substring which splits the values in one row of data (e.g. 
			SplitChar=',' for a .csv file, typically)
		RemoveChar: None
			If this is set to a string, each character in this string
			will be removed from the text prior to processing.
			
	Returns:
		numpy.recarray object
	
	'''
	intset = '0,1,2,3,4,5,6,7,8,9'.split(',')
	floatset = '0,1,2,3,4,5,6,7,8,9,.,-,e,+'.split(',')
	
	#read the files into an array of strings
	if isinstance(fname,np.ndarray):
		lines = fname
	elif isinstance(fname,list):
		lines = np.array(fname)
	else:
		lines = ReadASCIIFile(fname)
	
	#skip any lines that may not have any data
	if SkipLines > 0:
		lines = lines[SkipLines:]
	
	#get header if it exists
	if Header:
		head = lines[0]
		lines = lines[1:]
		
	#strip away some characters
	if isinstance(RemoveChar,str):
		chars = [l for l in RemoveChar]
		for i in range(0,lines.size):
			for c in chars:
				lines[i] = lines[i].replace(c,'')
	
	#get data dimensions (lines and columns)
	nl = np.size(lines)
	nc = np.size(lines[0].split(SplitChar))
	
	#split data into columns
	tmp = np.zeros(nl,dtype='object')
	ncol = np.zeros(nl,dtype='int32')
	for i in range(0,nl):
		tmp[i] = np.array((lines[i].strip('\n')).split(SplitChar))
		ncol[i] = tmp[i].size
	
	#create regular array
	tmpreg = np.zeros((nl,nc),dtype='object')
	for i in range(0,nl):
		tmpreg[i,:ncol[i]] = tmp[i]
		tmpreg[i,ncol[i]:] = ''
	
	if not Missing is None:
		if np.size(Missing) == 1:
			bad = np.where(tmpreg == Missing)
			tmpreg[bad] = ''
		else:
			for M in Missing:
				bad = np.where(tmpreg == M)
				tmpreg[bad] = ''	
	
	#sort the dtype out
	if not dtype is None:
		nd = len(dtype)
		nc = np.min([nc,nd])
		nd = nc
	else:
		#get the dtype names
		if Header:
			#replace newlines with nothing and tabs with spaces
			head = head.replace('\n','')
			if not SplitChar == '\t':
				head = head.replace('\t',' ')
			names = head.split(SplitChar)
			#remove spaces in names and '.' or ','
			for i in range(0,len(names)):
				names[i] = names[i].replace(' ','')
				names[i] = names[i].replace('.','')
				names[i] = names[i].replace(',','')
		else:
			names = []
			order = '{:d}'.format(np.int32((np.log10(nc)+1)//1))
			fmtstr = 'Col{:0'+order+'d}'
			for i in range(0,nc):
				names.append(fmtstr.format(i))
			
		#attempt an autodetect of the dtypes, this will probably be slow
		dtypes = []
		for i in range(0,nc):
			tmp_dt = 'int32'
			colchar = ''.join(tmpreg[:,i])
	
			uniqchar = np.array(list(set(colchar)))
			nchar = uniqchar.size
			
			if nchar > 14:
				#must not be a number, shall use string
				tmp_dt = 'string'
			else:
				#check for non numeric characters
				for j in range(0,nchar):
					if not uniqchar[j] in floatset:
						#can't be a number
						tmp_dt = 'string'
						break
				
				#now check for '.'
				if not tmp_dt == 'string':
					if '.' in uniqchar:
						tmp_dt = 'float32'
			
			#if it is a string, we must work out exactly what length is required
			if tmp_dt == 'string':
				tmpcol = tmpreg[:,i].astype('U')
				tmp_dt = tmpcol.dtype.str
				
			dtypes.append(tmp_dt)
			
		#assemble the dtypes
		dtype = []
		for i in range(0,nc):
			dtype.append((names[i],dtypes[i]))

	#by now we should have a dtype, so create output array
	out = np.recarray(nl,dtype=dtype)
	
	for i in range(0,nc):
		if 'int' in dtype[i][1] or 'float' in dtype[i][1]:
			bad = np.where(tmpreg[:,i] == '')[0]
			tmpreg[bad,i] = '0'
		if 'int' in dtype[i][1]:
			fv = FillValInt
		elif 'float' in dtype[i][1]:
			fv = FillValFloat
		else:
			fv = None
		out[dtype[i][0]] = tmpreg[:,i].astype(dtype[i][1])
		if not fv is None:
			out[dtype[i][0]][bad] = fv
	return out
	
		
		
			
		
		
	
	
