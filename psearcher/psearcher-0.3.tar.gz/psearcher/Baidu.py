from psearcher.BaseEngine import BaseEngine


class Baidu(BaseEngine):
    url = 'http://www.baidu.com/s'
    keyTag = 'word'
    pageTag = 'pn'
    startIndex = 0
    indexGap = 10

    def __init__(self, keyWord, amount=5, headers=None, timeout=60):

        self.name = 'Baidu'
        self.keyWord = keyWord
        self.amount = amount
        if headers:
            self.headers = headers
        self.timeout = timeout

    def getUrlParmas(self):
        url = self.url
        params = {
            self.keyTag: self.keyWord,
            self.pageTag: self.startIndex + self.indexGap*self.nextPage,
        }
        self.nextPage += 1
        return url, params


    def parser(self, soup):
        urls = []
        for div in soup.findAll('div', {'class': 'result'}):
            title = div.h3.a.getText()
            url = div.h3.a['href']
            urls.append({'title': title, 'link': url})

        return urls
