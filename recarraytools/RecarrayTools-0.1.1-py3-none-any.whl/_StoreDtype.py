import numpy as np
from . import __version__
import sys

#there are way too many of these, is there a function in numpy to do this?
dtypes = {	'?':('?',0),
			'b1':('?',0),
			'bool':('?',0),
			'bool_':('?',0),
			'bool8':('?',0),
			'Bool':('?',0),
			'int':('i',8),
			'int0':('i',8),
			'int_':('i',8),
			'int8':('i',1),
			'int16':('i',2),
			'int32':('i',4),
			'int64':('i',8),
			'Int8':('i',1),
			'Int16':('i',2),
			'Int32':('i',4),
			'Int64':('i',8),
			'intc':('i',4),
			'intp':('i',8),
			'i':('i',4),
			'i1':('i',1),
			'i2':('i',2),
			'i4':('i',4),
			'i8':('i',8),
			'l':('i',8),
			'long':('i',8),
			'longlong':('i',8),
			'p':('i',8),
			'q':('i',8),
			'h':('i',2),
			'short':('i',2),
			'b': ('i',1),
			'H': ('u',2),
			'I': ('u',4),
			'L': ('u',8),
			'P': ('u',8),	
			'UInt16': ('u',2),
			'UInt32': ('u',4),
			'UInt64': ('u',8),
			'UInt8': ('u',1),
			'Uint64': ('u',8),
			'u1': ('u',1),
			'u2': ('u',2),
			'u4': ('u',4),
			'u8': ('u',8),
			'ubyte': ('u',1),
			'uint': ('u',8),
			'uint0': ('u',8),
			'uint16': ('u',2),
			'uint32': ('u',4),
			'uint64': ('u',8),
			'uint8': ('u',1),
			'uintc': ('u',4),
			'uintp': ('u',8),
			'ulonglong': ('u',8),
			'ushort': ('u',2),
			'Float128': ('f',16),
			'Float16': ('f',2),
			'Float32': ('f',4),
			'Float64': ('f',8),
			'd': ('f',8),
			'double': ('f',8),
			'e': ('f',2),
			'f': ('f',4),
			'f16': ('f',16),
			'f2': ('f',2),
			'f4': ('f',4),
			'f8': ('f',8),
			'float': ('f',8),
			'float128': ('f',16),
			'float16': ('f',2),
			'float32': ('f',4),
			'float64': ('f',8),
			'float_': ('f',8),
			'g': ('f',16),
			'half': ('f',2),
			'longdouble': ('f',16),
			'longfloat': ('f',16),
			'single': ('f',4),
			'Complex128': ('c',32),
			'Complex32': ('c',8),
			'Complex64': ('c',16),
			'D': ('c',16),
			'F': ('c',8),
			'G': ('c',32),
			'c16': ('c',16),
			'c32': ('c',32),
			'c8': ('c',8),
			'cdouble': ('c',16),
			'cfloat': ('c',16),
			'clongdouble': ('c',32),
			'clongfloat': ('c',32),
			'complex': ('c',16),
			'complex128': ('c',16),
			'complex256': ('c',32),
			'complex64': ('c',8),
			'complex_': ('c',16),
			'csingle': ('c',8),
			'longcomplex': ('c',32),
			'singlecomplex': ('c',8),
			'str': ('U',0),
			'str0': ('U',0),
			'str_': ('U',0),
			'unicode': ('U',0),
			'unicode_': ('U',0),
			'U': ('U',-1),
			'Bytes0':('S',0),
			'S':('S',-1),
			'a':('S',-1),
			'bytes':('S',0),
			'bytes0':('S',0),
			'bytes_':('S',0),
			'string_':('S',0),}



def _StoreDtype(f,dtype):
	'''
	Store a data type within the first few bytes of a file.
	
	'''
	#this little mess of code will work out the dtype, endianness and 
	#number of bytes
	if sys.byteorder == 'little':
		bo = '<'
	else:
		bo = '>'
	ndt = len(dtype)
	end = np.zeros(ndt,dtype='U1') # endianness
	dtc = np.zeros(ndt,dtype='U1') # dtype code
	dln = np.zeros(ndt,dtype='int16')	# dtype number of bytes
	dnm = np.zeros(ndt,dtype='O') # name of each field
	dsh = np.zeros(ndt,dtype='O') # list of dimensions
	for i in range(0,ndt):
		dnm[i] = dtype[i][0]
		s = dtype[i][1]
		if s[0] in ['>','<','|']:
			end[i] = s[0]
			s = s[1:]
		else:
			end[i] = bo

		#work out the one letter code and number of bytes
		#default to object with 0 length
		if s[0] in ['U','S','a']:
			dtc[i] = s[0]
			if len(s) > 1:
				dln[i] = np.int16(s[1:])
			else:
				dln[i] = 1
		else:
			A = dtypes.get(s,('O',0))
			#dtc[i],dln[i] = dtypes.get(s,('O',0))
			dtc[i] = A[0]
			dln[i] = A[1]
	
		#get the shape
		if len(dtype[i]) == 3:
			dsh[i] = dtype[i][2]
		else:
			dsh[i] = None
	
	
	#first bit should be uint32 equal to 0 - this tells us either that
	#the file is empty, or there is a dtype stored within it - to tell
	#the difference, check that the file > 4 bytes long
	zero = np.uint32(0)
	zero.tofile(f)
	
	#now store the version of this object, just in case things change in 
	#future
	l = np.uint32(len(__version__))
	ver = np.array(__version__)
	l.tofile(f)
	ver.tofile(f)
	
	#store the dtypes, starting with the number of them
	np.uint32(ndt).tofile(f)
	#now the endianness, code, bytes
	end.tofile(f)
	dtc.tofile(f)
	dln.tofile(f)
	
	#save the shapes
	for i in range(0,ndt):
		if dsh[i] is None:
			np.int32(0).tofile(f)
		else:
			nsh = np.int32(len(dsh[i]))
			sh = np.int32(dsh[i])
			nsh.tofile(f)
			sh.tofile(f)
	
	#now the names
	for i in range(0,ndt):
		ld = np.uint32(len(dnm[i]))
		ld.tofile(f)
		np.array(dnm[i]).tofile(f)
		
	#done - I think
	return end,dtc,dln,dnm
		
	
	
