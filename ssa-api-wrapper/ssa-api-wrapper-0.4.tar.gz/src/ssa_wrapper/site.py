import requests
import json



def working():
  url = 'https://phoneguyapi.herokuapp.com/ssa/site'
  response = requests.get(url)
  json_data = json.loads(response.text)
  working = json_data['working']
  return working

def status():
   url = 'https://phoneguyapi.herokuapp.com/ssa/site'
   response = requests.get(url)
   json_data = json.loads(response.text)
   working = json_data['status']
   return working
