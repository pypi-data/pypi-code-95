import urllib
import requests
import json
import chardet
from LogService import LogServiceClass
import random,time
import urllib3
urllib3.disable_warnings()

class HttpServiceClass(object):
    Log = LogServiceClass(tag="HttpServiceClass")
    LogD = Log.LogD
    LogW = Log.LogW
    LogE = Log.LogE
    # 'accept-encoding': 'gzip, deflate, br',
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        # 'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        'user-agent': 'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; MI 4S Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.146 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.1.3',
    }

    params = {}

    def __init__(self):
        pass
    
    def GetUrlReset(self, url, timeout=60):
        res = urllib.request.urlopen(url, data=None, timeout=timeout)
        return res.read().decode()
    # proxies{"https":"127.0.0.1:12639","http":"127.0.0.1:12639"}
    def GetUrlResetDataByRequests(self, url, headers = None, params = None, data = None, stream = False, verify=False, timeout=60, proxies=False, isAutoEncoding=False):
        res = self.GetUrlResetByRequests(url, headers, params, data, stream, verify, timeout, proxies)
        dumpTab = None
        try:
            if res.ok:
                try:
                    if res.text != '':
                        dumpTab = json.loads(res.text)
                except BaseException as e:
                    self.LogE("GetUrlResetDataByRequests error ==>>  " + str(e))
                finally:
                    pass
            else:
                self.LogE("GetUrlResetDataByRequests error ==>>  " + res.text)
        except BaseException as e:            
            self.LogE("GetUrlResetDataByRequests BaseException error ==>> URL: {}  Error: {}".format(url, str(e)))
        return dumpTab
    
    def GetUrlResetByRequests(self, url, headers = None, params = None, data = None, stream = False, verify=False, timeout=60, proxies=False, isAutoEncoding=False):
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False
        res = None
        
        try:
            if headers:
                for headerItem in headers:
                    self.headers[headerItem] = headers[headerItem]
            requests.packages.urllib3.disable_warnings()
            res = s.get(url, headers = self.headers, params = params, data = data, verify=verify, stream=stream, timeout=timeout, proxies=proxies)
            if isAutoEncoding:
                res.encoding = chardet.detect(res.content).get('encoding')
            res.close()            
            return res
        except BaseException as e:            
            self.LogE("GetUrlResetByRequests BaseException error ==>> URL: {}  Error: {}".format(url, str(e)))        
        return res
    

        
    def PostUrlResetDataByRequests(self, url, headers = None, params = None, data = None, stream = False, files= False, verify=False, cookies=False, timeout=60, proxies=None, isAutoEncoding=False):
        res = self.PostUrlResetByRequests(url, headers, params, data, stream, files, verify, cookies, timeout, proxies)
        dumpTab = None
        try:
            if res.ok:
                try:
                    if res.text != '':
                        dumpTab = json.loads(res.text)
                except BaseException as e:
                    self.LogE("PostUrlResetDataByRequests error ==>>  " + str(e))
                finally:
                    pass
            else:
                self.LogE("PostUrlResetDataByRequests error ==>>  " + res.text)
        except BaseException as e:            
            self.LogE("PostUrlResetDataByRequests BaseException error ==>> URL: {}  Error: {}".format(url, str(e)))
        return dumpTab

    def PostUrlResetByRequests(self, url, headers = None, params = None, data = None, stream = False, files= False, verify=False, cookies=False, timeout=60, proxies=None, isAutoEncoding=False):
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False
        res = None
        
        try:
            if headers:
                for headerItem in headers:
                    self.headers[headerItem] = headers[headerItem]
            requests.packages.urllib3.disable_warnings()
            res = s.post(url, headers = self.headers, params = params, data = data, verify=verify, stream=stream, files= files, cookies=cookies, timeout=timeout, proxies=proxies)
            if isAutoEncoding:
                res.encoding = chardet.detect(res.content).get('encoding')
            res.close()            
            return res
        except BaseException as e:            
            self.LogE("PostUrlResetByRequests BaseException error ==>> URL: {}  Error: {}".format(url, str(e)))        
        return res
    