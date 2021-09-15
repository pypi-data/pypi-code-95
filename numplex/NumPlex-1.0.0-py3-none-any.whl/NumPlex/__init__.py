import numpy as np
import math
from math import sin, cos, tan, atan, sqrt, e
def ctp(a):
	b=a.copy()
	b.isPolar=True
	return b
def ctr(a):
	b=a.copy()
	b.isPolar=False
	return b
def ctc(a):
	return complex(a,0)
class complex:
	"""A complex number class compatible with Numpy"""
	def __init__(self, p1, p2,isPolar=False):
		self.isPolar=isPolar
		if (isPolar):
			self.r=p1
			self.theta=p2
			self.a=cos(self.theta)*self.r
			self.b=sin(self.theta)*self.r
		else:
			self.a = p1
			self.b = p2
			self.r=sqrt(self.a**2+self.b**2)
			try:
				self.theta=atan(self.b/self.a)
			except:
				self.theta=math.pi/2*abs(self.b)/self.b
		self.vconjugate = np.vectorize(self.conjugate)
		self.vc = self.vconjugate
		self._vadd=np.vectorize(self._add)
		self._va = self._vadd
		self._vsubtract=np.vectorize(self._subtract)
		self._vs = self._vsubtract
		self._vmultiply=np.vectorize(self._subtract)
		self._vm = self._vmultiply
		self._vdivide = np.vectorize(self._multiply)
		self._vd = self._vdivide
	def __getitem__(self, item):
		if item==0:
			return self.a
		elif item==1:
			return self.b
		elif item==2:
			return self.r
		elif item==3:
			return self.theta
		else:
			raise IndexError("Index out of range. Use 0 for x, 1 for y, 2 for r, and 3 for θ.")
	def copy(self):
		if self.isPolar:
			return complex(self.r,self.theta,True)
		else:
			return complex(self.a,self.b,False)
	def __repr__(self):
		if self.isPolar:
			return "("+str(self.r)+", "+str(self.theta)+")"
		return str(self.a)+"+"+str(self.b)+"i"
	def __str__(self):
		return self.__repr__()
	def __add__(self, other):
		return self._add(other)
	def __mul__(self, other):
		return self._multiply(other)
	def __rmul__(self, other):
		return self.__mul__(other)
	def __truediv__(self, other):
		return self._divide(other)
	def __floordiv__(self,other):
		return self._floordiv(other)
	def __div__(self,other):
		return self._divide(other)
	def __rdiv__(self,other):
		return self._divide(other)
	def __eq__(self, o):
		#is it equal to o?
		if type(o) == type(self):
			if self.isPolar:
				return self.theta==o.theta and self.r == o.r
			return self.a==o.a and self.b==o.b
		else:
			return False
	def __mod__(self, other):
		return self._mod(other)
	def __ne__(self, other):
		return not self.__eq__(other)
	def __IADD__(self,other):
		self=self._add(other)
	def __ISUB__(self,other):
		self=self._subtract(other)
	def __IMUL__(self,other):
		self=self._multiply(other)
	def __IDIV__(self,other):
		self=self._divide(other)
	def __IFLOORDIV__(self,other):
		self=self._floordiv(other)
	def __pow__(self,other):
		pass
	def _add(self,b):
		if type(b)==int or type(b)==float:
			b=complex(b,0)
		cplx = complex(self.a+b.a,self.b+b.b)
		if self.isPolar:
			return ctp(cplx)
		return cplx
	def _subtract(self,b):
		if type(b)==int or type(b)==float:
			b=complex(b,0)
		cplx=complex(self.a-b.a,self.b-b.b)
		if self.isPolar:
			return ctp(cplx)
		return cplx
	def _multiply(self,b):
		if type(b)==int or type(b)==float:
			b=complex(b,0)
		cplx = complex(self.a*b.a-self.b*b.b,self.a*b.b+self.b*b.a)
		if self.isPolar:
			return ctp(cplx)
		return cplx
	def _divide(self,b):
		if type(b)==int or type(b)==float:
			b=complex(b,0)
		return self._multiply(complex(b.conjugate().a/(b.a**2-b.b**2),b.conjugate().b/(b.a**2-b.b**2)))
	def _floordiv(self,b):
		if type(b)==int or type(b)==float:
			b=complex(b,0)
		complex(int(self._multiply(b).a),int(self._multiply(b).b))
	def _mod(self,b):
		if type(b)==int or type(b)==float:
			b=complex(b,0)
		return self-self._floordiv(b)*b
	def conjugate(self):
		return complex(self.a,-self.b)
	def __NEG__(self):
		return complex(-self.a,-self.b)
	def _pow(self,b):
		pass
	def __len__(self):
		return 0 if self.a == 0 and self.b == 0 else (2 if self.a !=0 and self.b!=0 else 1)
	def __invert__(self):
		return self.conjugate()
# -=	__ISUB__(SELF, OTHER)
# +=	__IADD__(SELF, OTHER)
# *=	__IMUL__(SELF, OTHER)
# /=	__IDIV__(SELF, OTHER)
# //=	__IFLOORDIV__(SELF, OTHER)
# %=	__IMOD__(SELF, OTHER)
# **=	__IPOW__(SELF, OTHER)
# >>=	__IRSHIFT__(SELF, OTHER)
# <<=	__ILSHIFT__(SELF, OTHER)
# &=	__IAND__(SELF, OTHER)
# |=	__IOR__(SELF, OTHER)
# ^=	__IXOR__(SELF, OTHER)
#https://www.geeksforgeeks.org/operator-overloading-in-python/
#nice dunder methods: https://builtin.com/data-science/dunder-methods-python
#all the math methods: https://www.tutorialsteacher.com/python/magic-methods-in-python
