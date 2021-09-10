import base64,binascii
from typing import Type,Optional,Literal
from gspread.models import Worksheet
import pickle
MAXIMUM_SIZE_OF_CELL = 50000-5
ALLOWED_TYPES_OF_VARIABLE_IN_SHEET = Literal['dict','object']
class SyncedVariable:
	def __init__(self,sheet:"Worksheet"):
		self._sheet:Worksheet = sheet
		self._value = Exception("abstract class")
	def __enter__(self):
		self.pull()
		return self._value
	def __exit__(self,type,value,traceback):
		self.push()
		return False
		
	def push(self):
		raise Exception("abstract class")	
	def pull(self):
		raise Exception("abstract class")


	@classmethod
	def from_wroksheet(cls,sheet:"Worksheet",type_of_var:Optional[ALLOWED_TYPES_OF_VARIABLE_IN_SHEET]=None) -> Type["SyncedVariable"]:
		#3.10 is not out yet soooo
		#match type_of_var:
		if type_of_var == 'dict':#	case 'dict':
			return SyncedDict(sheet)
		elif type_of_var == 'object':#	case 'object'
			return SyncedObject(sheet)
		else:#	case _:
			x,y = sheet.col_count,sheet.row_count
			#WHY THERE IS NO 3.10 YET????????
			if x == 1:
				return SyncedObject(sheet)
			if x == 2:
				return SyncedDict(sheet)
class SyncedDict(SyncedVariable):
	def __init__(self,sheet:"Worksheet"):
		super().__init__(sheet)

		self._sheet.resize(None,2)
		self._value:dict=dict()

		self.pull()
		
	
	def push(self)->"SyncedDict":
		k= [[f"{b}" for b in a] for a in self._value.items()]
		self._sheet.clear()
		self._sheet.resize(1,2)
		self._sheet.insert_rows(k)
		return self

	def pull(self)->"SyncedDict":
		for row in self._sheet.get_values():
			self._value[row[0]]=row[1]
		return self

	@property
	def dict(self):
		return self._value

	@dict.setter
	def dict(self, value:dict):
		if value is not dict:
			raise ValueError(f"{type(value)} is not a dict")
		self._value:dict=value





class SyncedObject(SyncedVariable):
	def __init__(self,sheet:"Worksheet"):
		super().__init__(sheet)
		self._sheet.resize(None,1)
		self._value = object()
		self.pull()
	def pull(self)->"SyncedObject":
		a = ""
		for value in self._sheet.col_values(1):
			a+=value
		try:
			self._value = pickle.loads(base64.b64decode(a))
		except(
			pickle.PickleError,
			binascii.Error,
			EOFError
		):#failed to decode, fall back to object()
			self._value = object()
			self.push()
		return self

	def push(self)->"SyncedObject":
		a = base64.b64encode(pickle.dumps(self._value)).decode("ascii")
		a = [ [a[i:i+MAXIMUM_SIZE_OF_CELL]] for i in range(0, len(a), MAXIMUM_SIZE_OF_CELL) ]
		self._sheet.clear()
		self._sheet.resize(1,1)
		self._sheet.insert_rows(a)
		return self

	@property
	def object(self):
		return self._value

	@object.setter
	def object(self, value):
		self._value = value