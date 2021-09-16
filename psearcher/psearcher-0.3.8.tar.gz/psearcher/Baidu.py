from psearcher.BaseEngine import BaseEngine


class Baidu(BaseEngine):
    url = 'http://www.baidu.com/s'
    keyTag = 'word'
    pageTag = 'pn'
    startIndex = 0
    indexGap = 10

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
