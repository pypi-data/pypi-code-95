import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .syncedDict import SyncedDict

SCOPE =["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]


class Storage:
	def __init__(self,credentials_filename:os.path,url):
		credits = ServiceAccountCredentials.from_json_keyfile_name(credentials_filename,SCOPE)
		client = gspread.authorize(credits)
		self.document = client.open_by_url(url)
	@property
	def var1(self) -> "SyncedDict":
		return SyncedDict(self.document.sheet1)