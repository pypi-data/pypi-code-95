from gspread.models import Worksheet
class SyncedVariable:
	def __init__(self,sheet:"Worksheet"):
		self._sheet = sheet
	
class SyncedDict(SyncedVariable):
	def __init__(self,sheet:"Worksheet"):
		super().__init__(sheet)

		self._sheet.resize(None,2)
		self.__dict=dict()

		self.pull()
		
	
	def push(self)->"SyncedDict":
		k= [[f"{b}" for b in a] for a in self.__dict.items()]
		self._sheet.clear()
		self._sheet.resize(1,2)
		self._sheet.insert_rows(k)
		return self

	def pull(self)->"SyncedDict":
		for row in self._sheet.get_values():
			self.__dict[row[0]]=row[1]
		return self


	def __dict__(self):
		return self.__dict
	def __getitem__(self,*a,**kw):
		return self.__dict.__getitem__(*a,**kw)
	def __setitem__(self,*a,**kw):
		return self.__dict.__setitem__(*a,**kw)
	def __delitem__(self,*a,**kw):
		return self.__dict.__del_(*a,**kw)

	
