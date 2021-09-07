import gspread
class SyncedDict:
	def __init__(self,sheet:"gspread.models.Worksheet"):
		self.sheet = sheet
		self.sheet.resize(None,2)
		self.dict=dict()
		for row in self.sheet.get_values():
			self.dict[row[0]]=row[1]
		
	
	def sync(self):
		
		k= [[f"{b}" for b in a] for a in self.dict.items()]
		print(k)
		self.sheet.clear()
		self.sheet.resize(1,2)
		self.sheet.insert_rows(k)
		

		return self

	def __dict__(self):
		return self.dict
	
	def __getitem__(self,*a,**kw):
		return self.dict.__getitem__(*a,**kw)
	def __setitem__(self,*a,**kw):
		return self.dict.__setitem__(*a,**kw)
	def __delitem__(self,*a,**kw):
		return self.dict.__del_(*a,**kw)

	
