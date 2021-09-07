import requests
import socket
import json
import os
import datetime
import threading
import time
from tqdm import tqdm
global serverurl
serverurl="http://52.91.40.112:5000/"
global global_user,done,response
global_user=""
done=False
response={}
def getargs(argss,kwargs):
    args={}
    i=0
    for a in argss:
        args[str(i)]=a
        i=i+1
    args.update(kwargs)
    return args
def get_links(pages):
    links=[]
    for i in range(0,len(pages)):
        links.append("link"+str(i))
    return links
def getipaddress():
    hostname = socket.gethostname()
    ipaddress = socket.gethostbyname(hostname)
    ipaddress=ipaddress.replace('.','-')
    return ipaddress
def gettheuserid():
    try:
        userid=getipaddress()
    except:
        userid="unknown"
    return userid
def set_api_key():
    global global_user
    userid=gettheuserid()
    global_user=userid
def fetch_progress():
    global global_user,progressurl
    headers = {'Content-type': 'application/json'}
    res=requests.post(url = serverurl+"get_scraper_progress", data = json.dumps({"user":global_user}), headers=headers)
    try:
        res=json.loads(res.text)
    except:
        res=res.text
    prog=res["progress"]
    res_return=res["response"]
    return prog,res_return
def show_progress():
    global done
    prog=0
    last=0
    res={}
    with tqdm(total=200, desc="Progress") as progress:
        while(prog!=100):
            last=prog
            try:
                prog,res=fetch_progress()
            except:
                pass
            if(res=="error" or prog=="error"):
                print("Something wrong happened")
                break
            time.sleep(2)
            final=prog-last
            if(final>0):
                progress.update(final+final)
        response=res
        done=True
    progress.close()

class scraper():
    def __init__(self):
        set_api_key()
    def train_version1(self,*argss):
        headers = {'Content-type': 'application/json'}
        links=get_links(argss)
        start_time = threading.Timer(1,show_progress)
        start_time.start()
        res=requests.post(url = serverurl+"start_training", data = json.dumps({"user":global_user,"pages":argss,"links":links,"is_pypi":True,"bot":"autoscraper"}), headers=headers, timeout=60*60)
        try:
            res=json.loads(res.text)
        except:
            res=res.text
        print("Build Scraper successfully")
        return res
    def train(self,*argss,**kwargs):
        global done
        headers = {'Content-type': 'application/json'}
        links=get_links(argss)
        args=getargs(argss,kwargs)
        data_send={"user":global_user,"pages":argss,"links":links,"is_pypi":True,"bot":"autoscraper"}
        data_send.update(args)
        start_time = threading.Timer(1,show_progress)
        start_time.start()
        try:
            res=requests.post(url = serverurl+"start_scraper", data = json.dumps(data_send), headers=headers, timeout=60*60)
            try:
                res=json.loads(res.text)
            except:
                res=res.text
            response=res
            done=True
        except:
            pass
        while(done==False):
            pass
        print("Build Scraper successfully")
        return res
    def scrape(self,*argss,**kwargs):
        global done
        done=False
        headers = {'Content-type': 'application/json'}
        links=get_links(argss)
        args=getargs(argss,kwargs)
        start_time = threading.Timer(1,show_progress)
        start_time.start()
        data_send={"user":global_user,"pages":argss,"links":links,"is_pypi":True,"bot":"autoscraper"}
        data_send.update(args)
        try:
            res=requests.post(url = serverurl+"start_scraper", data = json.dumps(data_send), headers=headers, timeout=60*60)
            try:
                res=json.loads(res.text)
            except:
                res=res.text
            response=res
            done=True
        except:
            pass
        while(done==False):
            pass
        print("Build Scraper successfully")
        return response
    def run_version1(self,*argss,**kwargs):
        headers = {'Content-type': 'application/json'}
        args=getargs(argss,kwargs)
        if("html" not in args):
            args["page"]=args["0"]
        else:
            args["page"]=args["html"]
        if("id" not in args):
            args["botid"]=args["1"]
        else:
            args["botid"]=args["id"]
        args["user"]=global_user
        res=requests.post(url = serverurl+"run_autoscraper", data = json.dumps(args), headers=headers,timeout=60*60)
        try:
            res=json.loads(res.text)
        except:
            res=res.text
        print("Run successfully")
        return res
    def run(self,*argss,**kwargs):
        headers = {'Content-type': 'application/json'}
        args=getargs(argss,kwargs)
        if("url" not in args):
            args["url"]=args["0"]
        if("id" not in args):
            args["botid"]=args["1"]
        else:
            args["botid"]=args["id"]
        args["user"]=global_user
        res=requests.post(url = serverurl+"run_autoscraper", data = json.dumps(args), headers=headers,timeout=60*60)
        try:
            res=json.loads(res.text)
        except:
            res=res.text
        print("Run successfully")
        return res
