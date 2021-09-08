# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

import json
import time
import pkg_resources

import six
from six.moves.urllib.parse import urlencode
import requests

from data2Insights.settings import DEFAULT_BASE_URL_FOR_TEXT
from data2Insights.settings import DEFAULT_BASE_URL_FOR_VISION

class Endpoint(object):
	
	def __init__(self,accountId,apikey,emailId, base_url1=DEFAULT_BASE_URL_FOR_VISION):

		self.accountId = accountId
		self.apikey = apikey
		self.emailId = emailId
		self.base_url1 = base_url1
	
	
		
class VisionClassifications(Endpoint):
	def logo(self, data):
		url = '{}'.format(self.base_url1)+"/"+"logo"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def bird(self, data):
		url = '{}'.format(self.base_url1)+"/"+"bird"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def transport(self, data):
		url = '{}'.format(self.base_url1)+"/"+"transport"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def plant(self, data):
		url = '{}'.format(self.base_url1)+"/"+"plant"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def gender(self, data):
		url = '{}'.format(self.base_url1)+"/"+"gender"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def emotion(self, data):
		url = '{}'.format(self.base_url1)+"/"+"emotion"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def color(self, data):
		url = '{}'.format(self.base_url1)+"/"+"color"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def age(self, data):
		url = '{}'.format(self.base_url1)+"/"+"age"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def scene(self, data):
		url = '{}'.format(self.base_url1)+"/"+"scene"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def tlo(self, data):
		url = '{}'.format(self.base_url1)+"/"+"tlo"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def violence(self, data):
		url = '{}'.format(self.base_url1)+"/"+"violence"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def weather(self, data):
		url = '{}'.format(self.base_url1)+"/"+"weather"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def generalobject(self, data):
		url = '{}'.format(self.base_url1)+"/"+"object"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def pet(self, data):
		url = '{}'.format(self.base_url1)+"/"+"pet"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def style(self, data):
		url = '{}'.format(self.base_url1)+"/"+"style"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def picturequality(self, data):
		url = '{}'.format(self.base_url1)+"/"+"picturequality"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?img="+data
		raw_responses = requests.get(url, data,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def logoupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"logo"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def birdupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"bird"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def transportupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"transport"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def plantupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"plant"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def sceneupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"scene"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def tloupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"tlo"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def violenceupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"violence"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def weatherupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"weather"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def genderupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"gender"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def emotionupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"emotion"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def ageupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"age"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def colorupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"color"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def generalobjectupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"object"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def petupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"pet"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def styleupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"style"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e

	def picturequalityupload(self,files):
		url = '{}'.format(self.base_url1)+"/"+"picturequality"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)
		raw_responses = requests.post(url, files=files,verify=False)
		if raw_responses.status_code == 200:
			return raw_responses.json()
		else:
			try:
				return raw_responses.status_code
			except Exception as e:
				return e



