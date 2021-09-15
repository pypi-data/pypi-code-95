from typing import Union

import parsel


def parse_products(html: str) -> list:
    sel = parsel.Selector(text=html)
    asin = sel.xpath("//@data-asin").getall()
    asin = list(filter(lambda s: s != '', asin))
    return asin


def parse_max_page(html: str) -> Union[int, None]:
    sel = parsel.Selector(text=html)
    max_page = sel.xpath("//ul[@class='a-pagination']/li[last()-1]/text()").get()
    if max_page and max_page.isdigit():
        return int(max_page)
    else:
        return None
