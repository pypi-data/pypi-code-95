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
	
	def __init__(self,accountId,apikey,emailId, base_url=DEFAULT_BASE_URL_FOR_TEXT):

		self.accountId = accountId
		self.apikey = apikey
		self.emailId = emailId
		self.base_url = base_url
	
	
	
class Classifications(Endpoint):
    def sentiment(self, data):
        url = '{}'.format(self.base_url)+"/"+"sentiment"+"/"+'{}'.format(self.accountId)+"/"+'{}'.format(self.apikey)+"/"+'{}'.format(self.emailId)+"?userinputdata="+data
        raw_responses = requests.get(url, data,verify=False)
        #print("code",raw_responses.status_code)
        #print("res",raw_responses)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def emotion(self, data):

        url = '{}'.format(self.base_url) + "/" + "emotion" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data
        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e



    def topic(self, data):

        url = '{}'.format(self.base_url) + "/" + "topic" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data
        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def spam(self, data):

        url = '{}'.format(self.base_url) + "/" + "spam" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data
        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def gender(self, data):

        url = '{}'.format(self.base_url) + "/" + "gender" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def age(self, data):

        url = '{}'.format(self.base_url) + "/" + "age" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data
        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def tweetsentiment(self, data):

        url = '{}'.format(self.base_url) + "/" + "tweetsentiment" + "/" + '{}'.format(
            self.accountId) + "/" + '{}'.format(self.apikey) + "/" + '{}'.format(
            self.emailId) + "?userinputdata=" + data
        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def personalitytraits(self, data):

        url = '{}'.format(self.base_url) + "/" + "personalitytraits" + "/" + '{}'.format(
            self.accountId) + "/" + '{}'.format(self.apikey) + "/" + '{}'.format(
            self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def entity(self, data):

        url = '{}'.format(self.base_url) + "/" + "entity" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e



    def keyword(self, data):

        url = '{}'.format(self.base_url) + "/" + "keyword" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data
        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e



    def tweetentity(self, data):

        url = '{}'.format(self.base_url) + "/" + "tweetentity" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e
    def urlextraction(self, data):

        url = '{}'.format(self.base_url) + "/" + "urlextraction" + "/" + '{}'.format(
            self.accountId) + "/" + '{}'.format(self.apikey) + "/" + '{}'.format(
            self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e



    def readability(self, data):

        url = '{}'.format(self.base_url) + "/" + "readability" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e



    def similarity(self, data1, data2):

        url = '{}'.format(self.base_url) + "/" + "similarity" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "/" + data1 + "/" + data2

        raw_responses = requests.get(url, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e
    def bertentity(self, data):

        url = '{}'.format(self.base_url) + "/" + "bertentity" + "/" + '{}'.format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def hemptopic(self, data):

        url = "{}".format(self.base_url) + "/" + "hemptopic" + "/" + "{}".format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?userinputdata=" + data
        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e


    def summarization(self, data):

        url = "{}".format(self.base_url) + "/" + "summarization" + "/" + "{}".format(
            self.accountId) + "/" + '{}'.format(self.apikey) + "/" + '{}'.format(
            self.emailId) + "?userinputdata=" + data

        raw_responses = requests.get(url, data, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e

    def QA(self, question, paragraph):

        url = "{}".format(self.base_url) + "/" + "Q&A" + "/" + "{}".format(self.accountId) + "/" + '{}'.format(
            self.apikey) + "/" + '{}'.format(self.emailId) + "?question=" + question + "&paragraph=" + paragraph

        raw_responses = requests.get(url, question, verify=False)
        if raw_responses.status_code==200:
            return raw_responses.json()
        else:
            try:
                return raw_responses.status_code
            except Exception as e:
                return e



