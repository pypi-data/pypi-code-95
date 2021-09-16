from psearcher.BaseEngine import BaseEngine
from  pprint import  pprint


class Baidu(BaseEngine):
    url = 'http://www.baidu.com/s'
    keyTag = 'word'
    pageTag = 'pn'
    startIndex = 0
    indexGap = 10

    def __init__(self, keyWord, amount=5, headers=None, timeout=60, proxy = ""):
        self.name = 'Baidu'
        self.keyWord = keyWord
        self.amount = amount
        if headers:
            self.headers = headers
        self.timeout = timeout

    def get_url_and_parmas(self):
        url = self.url
        params = {
            self.keyTag: self.keyWord,
            self.pageTag: self.startIndex + self.indexGap*self.nextPage,
        }
        return url, params

    def parser(self, soup):
        results = []
        tags = soup.find_all(class_="result")
        print(len(tags))
        for tag in tags:
            print(tag)
            link = tag.h3.a.get("href")
            title = tag.h3.text
            describe = tag.text
            result = {
                "link": link,
                "describe": describe,
                "title": title,
            }
            results.append(result)
        return results
