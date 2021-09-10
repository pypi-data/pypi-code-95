import os
from typing import Optional,Type,Union,Dict,Tuple
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from .synced import SyncedVariable,ALLOWED_TYPES_OF_VARIABLE_IN_SHEET


SCOPE = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
		 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


class Db:
	def __init__(self, credentials_filename: os.path, url:str):
		credits = ServiceAccountCredentials.from_json_keyfile_name(
			credentials_filename, SCOPE)
		client = gspread.authorize(credits)
		self.__document = client.open_by_url(url)
		self.__vars:Dict[str,Type[SyncedVariable]]=dict()

	@property
	def var1(self) -> Type[SyncedVariable]:
		return self.__vars[0]
		

	def __getitem__(self,item:"Union[str,Tuple[str,ALLOWED_TYPES_OF_VARIABLE_IN_SHEET]]") -> Type[SyncedVariable]:

	
		if isinstance(item,tuple):
			name,type_of_var = item
		elif isinstance(item,str):
			name,type_of_var = item,None
		else:
			raise ValueError("item wrong form")


		if self.__vars.get(name) is not None:
			return self.__vars[name]







		if (sheet:={sheet.title:sheet for sheet in self.__document.worksheets()}.get(name)) is None:
			sheet = self.__document.add_worksheet(name,1,1)
		self.__vars[name] = SyncedVariable.from_wroksheet(sheet,type_of_var)

		return self.__vars[name]