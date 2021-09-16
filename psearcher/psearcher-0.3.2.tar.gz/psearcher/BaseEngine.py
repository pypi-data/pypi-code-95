import requests
import time
import random
import traceback
from retry import retry
from bs4 import BeautifulSoup
from loger import log

class BaseEngine(object):
    name = 'BaseEngine'
    timeout = 60
    session = requests.session()
    keyWord = ''
    amount = 5
    searchType = 'base'
    results = []
    nextPage = 0
    typeKit = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",   
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"
    }

    def parser(self, soup):
        log('You must rewrite your parser!', 1)
        # raise NotImplementedError
        pass

    def get_url_and_parmas(self):
        log('You must rewrite your getUrlParmas!', 1)
        # raise NotImplementedError
        pass

    @retry(tries=3, delay=random.random()*2)
    def get_page_results(self, url, params):
     
        @retry(tries=3, delay=random.random()*2)
        def req(url, data):
            r = self.session.get(url, params=data, headers=self.headers)
            r.raise_for_status
            return r

        # 输出信息  
        log('{} {} {} {}'.format(self.name, self.keyWord, self.nextPage, len(self.results)))

        # 请求页面
        try:
            r = req(url, params)
        except Exception:
            log('Connection error!\n {}'.format(traceback.print_format_exc()), 2)
        else:
            soup = BeautifulSoup(r.text, 'html.parser')
            page_results = self.parser(soup)
            if len(page_results) == 0:
                log('page_results count is 0!', 2)
                log(r.url)
                with open('error.html', 'w') as f:
                    f.write(r.text)
                raise
            else:
                return page_results

    def search(self):
        start_time = time.time()
        while len(self.results) < self.amount:
            
            url, params = self.get_url_and_parmas()
            self.nextPage += 1
            
            # 检查超时
            if time.time() - start_time > self.timeout:
                log('Search Timeout!', 1)
                break
            # 检查数量
            elif len(self.results) > self.amount:
                log("search Done", 1)
                break

        return self.results
