# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from data2Insights.settings import DEFAULT_BASE_URL_FOR_TEXT
from data2Insights.settings import DEFAULT_BASE_URL_FOR_Batch
from data2Insights.base1 import Classifications
from data2Insights.base2 import VisionClassifications
from data2Insights.base3 import BatchClassifications

from data2Insights.settings import DEFAULT_BASE_URL_FOR_VISION

class data2insights(object):
	def __init__(self,accountId,apikey,emailId, base_url=DEFAULT_BASE_URL_FOR_TEXT,base_url1=DEFAULT_BASE_URL_FOR_VISION,base_url3=DEFAULT_BASE_URL_FOR_Batch):

		self.accountId = accountId
		self.apikey = apikey
		self.emailId = emailId
		self.base_url = base_url
		self.base_url1 = base_url1
		self.base_url3 = base_url3


	@property
	def classifiers(self):
		if not hasattr(self, '_classifiers'):
			self._classifiers = Classifications(accountId=self.accountId,apikey=self.apikey,emailId=self.emailId,base_url=self.base_url)
			
		return self._classifiers


	@property
	def visionclassifiers(self):
		if not hasattr(self, '_visionclassifiers'):
			self._visionclassifiers = VisionClassifications(accountId=self.accountId,apikey=self.apikey,emailId=self.emailId,base_url1=self.base_url1)
		
		return self._visionclassifiers
    
	@property
	def batchclassifiers(self):
		if not hasattr(self,'_batchclassifiers'):
			self._batchclassifiers=BatchClassifications(accountId=self.accountId,apikey=self.apikey,emailId=self.emailId,base_url3=self.base_url3)
		return self._batchclassifiers