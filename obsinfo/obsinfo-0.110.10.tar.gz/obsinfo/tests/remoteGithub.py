import requests
import base64
import json

from ..misc import yamlref


def constructURL(user = "404",repo_name= "404",path_to_file= "404",url= "404"):
  url = url.replace("{user}",user)
  url = url.replace("{repo_name}",repo_name)
  url = url.replace("{path_to_file}",path_to_file)
  return url

json_url ='https://api.github.com/repos/larean/obsinfo/contents/obsinfo/_examples/Information_Files/campaign/BBOBS.INSU-IPGP.network.yaml?ref=v0.108'

#json_url = constructURL(user,repo_name,path_to_file,json_url) #forms the correct URL
response = requests.get(json_url) #get data from json file located at specified URL 

if response.status_code == requests.codes.ok:
    jsonResponse = response.json()  # the response is a JSON
    #the JSON is encoded in base 64, hence decode it
    content = base64.b64decode(jsonResponse['content'])
    #convert the byte stream to string
    jsonString = content.decode('utf-8')
    print(jsonString)
    finalJson = yamlref.loads(jsonString, base_uri = json_url)
else:
    print('Content was not found.')
    exit()

#for key, value in finalJson.items():
    #print("The key and value are ({}) = ({})".format(key, value))