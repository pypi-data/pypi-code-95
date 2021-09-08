# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

import json
import time
import pkg_resources

import six
from six.moves.urllib.parse import urlencode
import requests


from data2Insights.settings import DEFAULT_BASE_URL_FOR_Batch

class Endpoint(object):
	
	def __init__(self,accountId,apikey,emailId, base_url3=DEFAULT_BASE_URL_FOR_Batch):

		self.accountId = accountId
		self.apikey = apikey
		self.emailId = emailId
		self.base_url3 = base_url3
	
	
	
class BatchClassifications(Endpoint):
    '''def sentiment(self,files):
        #url = "https://batch.test.data2insights.ai/Batch/emotion/2/$2y$10$w7D3XOySMmGOK76R2y///beumMFtD9lQMz2dBwtT39nGZPTCnLSLeHS//bmakkala@aadhya-analytics.comm?select=1"
        '{}'.format(self.base_url3)='https://batch.test.data2insights.ai/Batch'
        url ='{}'.format(self.base_url3)+"/"+"sentiment"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?select=1"
        payload={}
        print(url)
        raw_responses = requests.post(url, data=payload, files=files)
        response=data2InsightsResponse()
        response.add_raw_response(raw_responses)
        return {'response':"hai"}'''

    def sentiment(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "sentiment" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def emotion(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "emotion" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def topic(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "topic" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def spam(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "spam" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def gender(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "gender" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def age(self, column, files):
      
        url = '{}'.format(self.base_url3) + "/" + "age" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def personalitytraits(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "personalitytraits" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def tweetsentiment(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "tweetsentiment" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def keyword(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "keyword" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def entity(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "entity" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def tweetentity(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "tweetentity" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def readability(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "readability" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def QA(self, column1, column2, files):
        
        url = '{}'.format(self.base_url3) + "/" + "Q&A" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(
            self.emailId) +"?select="+column1+"&select1="+column2
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def bertentity(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "bertentity" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def hemptopic(self, column, files):
        
        url = '{}'.format(self.base_url3) + "/" + "hemptopic" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?select=" + column
        payload = {}
        raw_responses = requests.post(url, data=payload, files=files)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e



        


	
