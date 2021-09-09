from datakund_scraper import *
import json
link1='https://www.shopclues.com/online-sale.html?sort_by=newarrivals&sort_order=desc&seo_name=online-sale&bsid%5b%5d=87&bsid%5b%5d=89&bsid%5b%5d=282&bsid%5b%5d=5926&product_rating%5b%5d=4.00-5.00&fsrc=product_rating'
link2='https://www.shopclues.com/online-sale.html?sort_by=newarrivals&sort_order=desc&seo_name=online-sale&bsid%5b%5d=628&bsid%5b%5d=480&bsid%5b%5d=34572&bsid%5b%5d=40442&bsid%5b%5d=633&product_rating%5b%5d=4.00-5.00&fsrc=product_rating'
link1="https://pypi.org/search/?q=requests"
link2="https://pypi.org/search/?q=firebase"
response=scraper.train(link1,link2)
print(response.keys())
res=scraper.run(link1,id=response["id"])
#res=scraper.run(link2,id="QJP4LW2EBTQM45N")
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
