import json
import urllib
from urllib.request import urlopen

class Generator:

 def __init__(self, link):
     self.link = link

 def Generate(self):
     url = f'{self.link}'
     with urlopen("https://api.lrl.kr/v2/short/?url=https://example.com&format=json") as url:
      data = url.read()
     load_data = json.loads(data.decode('utf-8'))
     result = load_data.get("url")
     return result