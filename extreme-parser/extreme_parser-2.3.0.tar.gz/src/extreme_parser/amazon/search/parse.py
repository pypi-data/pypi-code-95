import parsel


def parse_products(html: str) -> list:
    sel = parsel.Selector(text=html)
    asin = sel.xpath("//@data-asin").getall()
    asin = list(filter(lambda s: s != '', asin))
    return asin
