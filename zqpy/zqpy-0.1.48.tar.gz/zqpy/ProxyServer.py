from HttpService import HttpServiceClass
from TimeService import TimeServiceClass
from FileService import FileServiceClass
from LogService import LogServiceClass
from RegexService import RegexServiceClass
from bs4 import BeautifulSoup
import enum,json,time
# https://www.cnblogs.com/xiaonq/p/8044211.html
# https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/

class ProxySourceType(enum.Enum):
    XICI = 'XICI',
    IP66 = 'IP66',
    KUAIDAILI = 'KUAIDAILI',

class ProxyServerClass():
    def __init__(self):
        self.http = HttpServiceClass()
        self.time = TimeServiceClass()
        self.file = FileServiceClass()
        self.log = LogServiceClass()
        self.regex = RegexServiceClass()
        # self.url = 'http://www.66ip.cn/{}.html'
        # self.url = 'https://www.kuaidaili.com/free/inha/{}/'
        self.config = {}
        self.config[ProxySourceType.XICI] ={
            'name': ProxySourceType.XICI,
            'urlList': [
                'https://www.xicidaili.com/nn/{}',
                'https://www.xicidaili.com/nt/{}',
                'https://www.xicidaili.com/wn/{}',
                'https://www.xicidaili.com/wt/{}',
            ],
            'reName': 'tr',
            'reClass': 'odd',
            'reId': None,
            'reSubName': 'td',
        }
        self.config[ProxySourceType.IP66] ={
            'name': ProxySourceType.IP66,
            'urlList': [
                'http://www.66ip.cn/{}.html',
            ],
            'reName': 'tr',
            'reClass': None,
            'reId': None,
            'reSubName': 'td',
        }

    # 抓取某个来源得代理
    def get_all_proxy_by_type(self, proxySourceType, isForce=False):
        proxyList = []
        fileName = './%s-%s.json'%(proxySourceType.name, self.time.GetCurrDayZeroTime(True))
        if self.file.Exists(fileName) and not isForce:
            return json.loads(self.file.ReadFile(fileName))
        config = self.config.get(proxySourceType)
        if not config:
            return False
        self.log.LogD('开始抓取 %s 代理'%config['name'])
        for url in config['urlList']:
            result = self.http.GetUrlResetByRequests(url.format(1), isAutoEncoding = True)
            if result.status_code != 200:
                continue
            soup = BeautifulSoup(result.text, 'html.parser')
            allPageNum = 1
            for item in soup.find_all('a'):
                number = item.text
                if number.isdigit():
                    number = int(number)
                    allPageNum = number if number>allPageNum else allPageNum
            for pageIndex in range(1, allPageNum):
                time.sleep(2)
                result = self.http.GetUrlResetByRequests(url.format(pageIndex), isAutoEncoding = True)
                if result.status_code != 200:
                    continue
                soup = BeautifulSoup(result.text, 'html.parser')
                # print(soup.find_all(config['reName'], id=config['reId'], class_=config['reClass']))
                for item in soup.find_all(config['reName'], id=config['reId'], class_=config['reClass']):
                    # print(item)
                    data = {
                        'type':'',
                        'ip':'',
                        'port':'',
                        'isAnonymous':False,
                        'position':'',
                    }
                    index = 0
                    for itemd in item.find_all(config['reSubName']):
                        text = itemd.text
                        if '高匿' in text or '透明' in text:
                            data['isAnonymous'] = '高匿' in text
                        elif 'http' in text.lower():
                            data['type'] = 'HTTP' if 'http' == text.lower() else 'HTTPS'
                        elif text in self.regex.GetRegexIP(text):
                            data['ip'] = text
                        elif text.isdigit():
                            data['port'] = int(text)
                        else:
                            if index==3 and config['name']==ProxySourceType.XICI:
                                data['position'] = text.replace('\n','')
                        index += 1
                    if not data in proxyList and data.get('ip') != '':
                        proxyList.append(data)
                if pageIndex+1 == allPageNum:
                    percent = 100.0
                    print('%s 代理收集完成 : %s [%d/%d]'%(url, str(percent)+'%',pageIndex+1,allPageNum), end='\n')
                else:
                    percent = round(1.0 * pageIndex / allPageNum * 100,2)
                    print('%s 代理正在收集 : %s [%d/%d]'%(url, str(percent)+'%',pageIndex+1,allPageNum), end='\r')
            '''
            self.log.LogD('开始检查 %s 代理'%config['name'])
            for proxyIndex in range(len(proxyList)-1, -1, -1):
                result = self.http.GetUrlResetByRequests('https://www.baidu.com', timeout=3, proxies={proxyList[proxyIndex]['type']:'%s:%s'%(proxyList[proxyIndex]['ip'],proxyList[proxyIndex]['port'])})
                if not result or result.status_code != 200:
                    proxyList.remove(proxyList[proxyIndex])
            self.log.LogD('结束检查 %s 代理'%config['name'])
            self.log.LogD('%s 可用代理'%proxyList)
            '''

        self.file.WriteFile(fileName, json.dumps(proxyList))
        self.log.LogD('结束抓取 %s 代理'%config['name'])
        return proxyList
        
    # 收集所有得代理
    def collect_all_proxy(self):
            for proxySourceType in ProxySourceType:
                self.get_all_proxy_by_type(proxySourceType)
if __name__ == "__main__":
    ProxyServerClass().collect_all_proxy()