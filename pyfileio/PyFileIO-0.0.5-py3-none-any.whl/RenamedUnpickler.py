import io
import pickle

class RenamedUnpickler(pickle._Unpickler):
	'''
	I do not take credit for this function, if it works then thank the 
	person who wrote this post!
	https://stackoverflow.com/a/53327348
	'''

	def __init__(self,file, *, fix_imports=True, encoding='ASCII', errors='strict',OldNames=[],NewNames=[],Verbose=True):
		self._RUP_OldNames = OldNames
		self._RUP_NewNames = NewNames
		self._RUP_Verbose = Verbose
		self._RUP_NameMap = {}
		for i in range(0,len(OldNames)):
			self._RUP_NameMap[OldNames[i]] = NewNames[i]
		
		super(RenamedUnpickler,self).__init__(file, fix_imports=fix_imports, encoding=encoding, errors=errors)
			
	def find_class(self, module, name):
		if module in self._RUP_OldNames:
			#check if it is a straight replacement
			renamed_module = self._RUP_NameMap[module]
		else:
			#check each one
			renamed_module = module
			for n in self._RUP_OldNames:
				if module.startswith(n):
					renamed_module = self._RUP_NameMap[n]
		if self._RUP_Verbose:
			print('Renamed {:s} -> {:s}'.format(module,renamed_module))
		return super(RenamedUnpickler, self).find_class(renamed_module, name)

	

def RenamedLoad(file_obj,fix_imports=True, encoding='ASCII', errors='strict',OldNames=[],NewNames=[],Verbose=True):
	'''
	I do not take credit for this function, if it works then thank the 
	person who wrote this post!
	https://stackoverflow.com/a/53327348
	'''
    
	return RenamedUnpickler(file_obj,fix_imports=fix_imports,encoding=encoding,errors=errors,OldNames=OldNames,NewNames=NewNames,Verbose=Verbose).load()


def RenamedLoads(pickled_bytes,fix_imports=True, encoding='ASCII', errors='strict',OldNames=[],NewNames=[],Verbose=True):

	'''
	I do not take credit for this function, if it works then thank the 
	person who wrote this post!
	https://stackoverflow.com/a/53327348
	'''

	file_obj = io.BytesIO(pickled_bytes)
	return RenamedLoad(file_obj,fix_imports=fix_imports,encoding=encoding,errors=errors,OldNames=OldNames,NewNames=NewNames,Verbose=Verbose)
