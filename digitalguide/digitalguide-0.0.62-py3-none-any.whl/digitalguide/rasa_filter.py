from telegram.ext import MessageFilter
import requests as req
from requests.exceptions import Timeout
from configparser import ConfigParser 
  
config = ConfigParser() 
config.read('config.ini')

class FilterRasa(MessageFilter):
    def __init__(self, intent, confidence=0.8):
        self.intent = intent
        self.confidence = confidence
        
    def filter(self, message):
        try:
            response = req.post(config["rasa"]["url"] + "/model/parse", json={"text":message.text,
                                                                     "message_id":message.message_id}, timeout = (3, 8))
        except Timeout:
            False
        else:
            if not response.ok:
                return False                                                         
            return response.json()["intent"]["name"] == self.intent and response.json()["intent"]["confidence"] >= self.confidence