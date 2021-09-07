def WriteASCIIFile(fname,data):
	'''
	This procedure will write a list of strings to a file.
	
	Inputs: 
		fname: name and path of output file
		data: list or array of strings to write
	'''
	
	f = open(fname,'w')
	f.writelines(data)
	f.close()
