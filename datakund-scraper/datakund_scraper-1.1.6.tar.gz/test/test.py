from datakund_scraper import *
import json
link='https://www.google.com/search?q=shoes&rlz=1C1UEAD_enIN966IN966&oq=shoes&aqs=chrome.0.69i59j69i57j0i271l2j69i60l4.609j0j4&sourceid=chrome&ie=UTF-8'
#response=scraper.train(url=link)
#print(response["id"])
#response=scraper.run(url=link,id=response["id"])
response=scraper.run(url=link,id="TG67K0DK04R8XTJ")
print("response keys",response.keys())
with open ("data.json","w",encoding="utf-8") as d:
    d.write(json.dumps(response,sort_keys=False))
    
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