import os
from typing import Optional,Type
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .synced import SyncedVariable,SyncedDict


SCOPE = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
		 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


class Storage:
	def __init__(self, credentials_filename: os.path, url:str):
		credits = ServiceAccountCredentials.from_json_keyfile_name(
			credentials_filename, SCOPE)
		client = gspread.authorize(credits)
		self.__document = client.open_by_url(url)
		self.__var1:Optional[Type[SyncedVariable]]=None

	@property
	def var1(self) -> Type[SyncedVariable]:
		if self.__var1 is None:
			self.__var1 = SyncedDict(self.__document.sheet1)
		return self.__var1
		
