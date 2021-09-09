from datakund_scraper import *
import json
link1='https://pypi.org/search/?q=datakund&o='
link2='https://pypi.org/search/?q=firebase&o='
#response=scraper.train(link1,link2)
#print(response["id"])
#res=scraper.run(url=link1,id=response["id"])
res=scraper.run(link1,id="0MPFMDSFPKE761B")
print("response keys",res.keys())
with open ("data.json","w",encoding="utf-8") as d:
    d.write(json.dumps(res,sort_keys=False,indent=4))
    
'''
import json
import datetime
def read_file(file):
    with open(file+".txt",encoding="utf-8") as d:
        html=d.read()
    return html
print(datetime.datetime.now())
html1=read_file("html1")
html2=read_file("html2")
res=scraper.train(html1,html2)
#res=scraper.run(html=html1,id="NUT7D6M49OTWUBT")
print("res",res)
print(datetime.datetime.now())
'''

from datakund_scraper import *
import json
link1='https://pypi.org/search/?q=datakund&o='
link2='https://pypi.org/search/?q=firebase&o='
response=scraper.train(link1,link2)
res=scraper.run(link1,id=response["id"])
