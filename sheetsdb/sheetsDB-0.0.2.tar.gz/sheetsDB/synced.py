from gspread.models import Worksheet
class SyncedVariable:
	def __init__(self,sheet:"Worksheet"):
		self._sheet = sheet
	def __enter__(self):
		self.pull()
		return self
	def __exit__(self,type,value,traceback):
		self.push()
		return False
		
	def push(self):
		raise Exception("abstract class")	
	def pull(self):
		raise Exception("abstract class")
		
class SyncedDict(SyncedVariable):
	def __init__(self,sheet:"Worksheet"):
		super().__init__(sheet)

		self._sheet.resize(None,2)
		self._dict=dict()

		self.pull()
		
	
	def push(self)->"SyncedDict":
		k= [[f"{b}" for b in a] for a in self._dict.items()]
		self._sheet.clear()
		self._sheet.resize(1,2)
		self._sheet.insert_rows(k)
		return self

	def pull(self)->"SyncedDict":
		for row in self._sheet.get_values():
			self._dict[row[0]]=row[1]
		return self

	@property
	def dict(self):
		return self._dict

	def __enter__(self):
		super().__enter__()
		return self._dict