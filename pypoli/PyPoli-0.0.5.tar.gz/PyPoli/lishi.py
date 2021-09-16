import requests
import datetime

def ls_sj():
    res_ls = requests.get('https://api.iyk0.com/lishi/')

    json_ls = res_ls.json()

    y = (datetime.datetime.now().month)
    r = (datetime.datetime.now().day)
    ry = '0{}月0{}日'.format(y,r)
    list_ls = json_ls[ry]
    #print(list_ls)
    print("今天是：",ry)
    print("历史事件是：")
    for i in list_ls:
        print("\n\t",i["year"])
        print("\t",i["title"])
