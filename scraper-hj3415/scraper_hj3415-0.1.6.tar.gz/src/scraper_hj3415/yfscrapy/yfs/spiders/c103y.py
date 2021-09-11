import scrapy
import pandas as pd
from yfs import items

# cmd usage : scrapy crawl c103y -a ticker=tsla


class C103ySpider(scrapy.Spider):
    name = 'c103y'
    allowed_domains = ['finance.yahoo.com']

    def __init__(self, ticker: str):
        super().__init__()
        self.ticker = ticker

    def start_requests(self):
        urls = {
            '손익계산서': f'https://finance.yahoo.com/quote/{self.ticker}/financials?p={self.ticker}',
            '재무상태표': f'https://finance.yahoo.com/quote/{self.ticker}/balance-sheet?p={self.ticker}',
            '현금흐름표': f'https://finance.yahoo.com/quote/{self.ticker}/cash-flow?p={self.ticker}'
        }

        for title, url in urls.items():
            yield scrapy.Request(url=url, callback=self.parse_y, cb_kwargs=dict(title=''.join([title, 'y'])))

    def parse_y(self, response, title):
        common_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div'

        # 컬럼의 갯수(col_num)와 컬럼의 타이틀을 추출한다.
        col_titles = []
        for i in range(2, 10):
            t = response.xpath(''.join([common_xpath, f'/div[1]/div/div[{i}]/span/text()'])).get()
            if t is None:
                col_num = i
                self.logger.info(f'col_num : {i}')
                break
            else:
                col_titles.append(t)
        self.logger.info(f'col_titles : {col_titles}')

        # 열의 갯수(row_num)와 열의 타이틀을 추출한다.
        row_titles = []
        # row title
        for i in range(1, 50):
            t = response.xpath(''.join([common_xpath, f'/div[2]/div[{i}]/div[1]/div[1]/div[1]/span/text()'])).get()
            if t is None:
                row_num = i
                self.logger.info(f'row_num : {i}')
                break
            else:
                row_titles.append(t)
        self.logger.info(f'row_titles : {row_titles}')

        # 값데이터를 추출하고 데이터프레임을 만들기 위해 열타이틀을 key 로 하고 값데이터 리스트를 value 로 하는 딕셔너를 만든다.
        df_dict = {}
        for col in range(2, col_num):
            value_list = []
            for row in range(1, row_num):
                t = response.xpath(
                    ''.join([common_xpath, f'/div[2]/div[{row}]/div[1]/div[{col}]/span/text()'])).get()
                value_list.append(t)
            df_dict[col_titles[col - 2]] = value_list

        df = pd.DataFrame(data=df_dict, index=row_titles)

        # make item to yield
        item = items.C103items()
        item['ticker'] = self.ticker
        item['title'] = title  # 손익계산서y, 재무상태표y, 현금흐르표y
        item['df'] = df

        print(item['df'])
        print(f"ticker : {item['ticker']} / title : {item['title']}")

        yield item
