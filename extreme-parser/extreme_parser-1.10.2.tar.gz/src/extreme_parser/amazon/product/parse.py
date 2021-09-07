import re
from typing import Union, Dict

import js2py
import js2py.internals.simplex
import numpy
import pandas
import parsel

from extreme_parser.amazon.product.model import Product
from extreme_parser.util.parse import parse_number


def product_overview_feature_div_table(selector: parsel.Selector, field: str) -> str:
    table = selector.xpath("//div[@id='productOverview_feature_div']//table").get()
    if table is None:
        return ""
    table = pandas.read_html(table)
    if len(table) <= 0:
        return ""
    table = table[0].set_index(0)
    if field not in table[1]:
        return ""
    s = table[1][field]
    return s


def product_details_table(selector: parsel.Selector, field: str) -> str:
    table = selector.xpath(
        "//table[@id='productDetails_detailBullets_sections1']|"
        "//table[@id='productDetails_techSpec_section_1']"
    ).get()
    if table is None:
        return ""
    table = pandas.read_html(table)
    if len(table) <= 0:
        return ""
    table = table[0].set_index(0)
    if field not in table[1]:
        return ""
    s = table[1][field]
    return s


def parse(html: str, p: Product):
    sel = parsel.Selector(text=html)
    parse_product_asin(p, selector=sel)
    parse_parent_asin(p, selector=sel)
    parse_weight(p, selector=sel)
    parse_brand(p, selector=sel)
    parse_price(p, selector=sel)
    parse_in_stock(p, selector=sel)
    parse_stock(p, selector=sel)
    parse_ship_day(p, selector=sel)
    parse_ship(p, selector=sel)
    parse_delivery(p, selector=sel)
    parse_material(p, selector=sel)
    parse_description(p, selector=sel)
    parse_title(p, selector=sel)
    parse_size(p, selector=sel)
    parse_color(p, selector=sel)
    parse_variation(p, selector=sel)


def parse_product_asin(p: Product, selector: parsel.Selector = None):
    p.product_asin = selector.re_first(r'"productAsin":"(.+?)"')


def parse_parent_asin(p: Product, selector: parsel.Selector = None):
    p.parent_asin = selector.re_first(r'"parentAsin":"(.+?)"')


def parse_weight(p: Product, selector: parsel.Selector = None):
    def s1() -> str:
        return product_details_table(selector, "Item Weight")

    def s2() -> str:
        ul = selector.xpath("//div[@id='detailBullets_feature_div']/ul")
        s = ul.xpath("//span[contains(text(), 'Item Weight')]/following-sibling::span[1]/text()").get()
        s = s or ul.xpath(
            "substring-after(//span[contains(text(), 'Product Dimensions')]/following-sibling::span[1]/text(), '; ')"
        ).get("")
        return s

    weight_str = s1() or s2()
    if weight_str == "":
        p.weight = None
        return
    weight: Union[None, int, float] = parse_number(weight_str)
    if weight is None:
        p.weight = None
        return

    if weight_str.endswith("ounces") or weight_str.endswith("Ounces"):
        p.weight = weight * 0.0625
    elif weight_str.endswith("pounds") or weight_str.endswith("Pounds"):
        p.weight = float(weight)
    else:
        p.weight = None
        return


def parse_brand(p: Product, selector: parsel.Selector = None):
    def s1() -> str:
        return product_overview_feature_div_table(selector, "Brand")

    def s2() -> str:
        s = selector.xpath("//a[@id='bylineInfo']/text()").re_first("Brand: (.*)")
        s = s or selector.xpath("//a[@id='bylineInfo']/text()").re_first("Visit the (.*) Store")
        return s

    brand = s1() or s2()
    if brand == "":
        p.brand = None
        return

    p.brand = brand


def parse_price(p: Product, selector: parsel.Selector = None):
    def table() -> pandas.DataFrame:
        t = pandas.DataFrame(index=("origin", "discount"), columns=('title', 'price'))
        for i, tr in enumerate(selector.xpath("//div[@id='price']/table/tr")[:2]):
            t.iat[i, 0] = tr.xpath("normalize-space(./td[1]/text())").get()
            t.iat[i, 1] = tr.xpath("normalize-space(./td[2]/span[1]/text())").get()
        return t

    def s1() -> str:
        s = selector.xpath("//span[@id='priceblock_ourprice']/text()").get()
        s = s or selector.xpath("//span[@id='priceblock_saleprice']/text()").get()
        s = s or selector.xpath("//div[@id='buyNew_noncbb']/span/text()").get()
        s = s or selector.xpath("//*[@id='color_name_0_price']/span/text()[last()]").get()
        return s or ""

    def s2() -> str:
        t = table()
        if numpy.all(t["price"] == ""):
            return ""
        if numpy.any(t["price"] == ""):
            return str(t["price"][t["price"] != ""][0])
        if t.at["discount", "title"] == "Deal of the Day:":
            return str(t.at["origin", "price"])
        else:
            return str(t.at["discount", "price"])

    prices_str = s1() or s2()
    prices: Union[None, list] = parse_number(prices_str.replace(",", ""), first=False)
    if prices is None or len(prices) == 0:
        p.price_min = None
        p.price_max = None
    elif len(prices) == 1:
        p.price_min = None
        p.price_max = float(prices[0])
    else:
        p.price_min = float(prices[0])
        p.price_max = float(prices[1])


def parse_in_stock(p: Product, selector: parsel.Selector = None):
    in_stock = selector.xpath("//div[@id='availability']/span/text()").get()
    if in_stock is None:
        p.in_stock = None
        return

    in_stock = in_stock.strip()
    if (
        in_stock == "In Stock." or
        in_stock.startswith("Only") or
        in_stock.startswith("Usually") or
        in_stock.startswith("Available")
    ):
        p.in_stock = True
    elif in_stock in ["In stock soon.", "Currently unavailable.", "Temporarily out of stock.", ""]:
        p.in_stock = False
    else:
        p.in_stock = None


def parse_stock(p: Product, selector: parsel.Selector = None):
    stock = selector.xpath("//div[@id='availability']/span/text()").get()
    if stock is None:
        p.stock = None
        return
    stock = stock.strip()
    if not stock.startswith("Only"):
        p.stock = None
        return

    p.stock = parse_number(stock)


def parse_ship_day(p: Product, selector: parsel.Selector = None):
    ship_day = selector.xpath("//div[@id='availability']/span/text()").re(r"Usually ships within (\d+) to (\d+) days.")
    if len(ship_day) < 2:
        p.ship_day_min = None
        p.ship_day_max = None
    else:
        p.ship_day_min = int(ship_day[0])
        p.ship_day_max = int(ship_day[1])


def parse_ship(p: Product, selector: parsel.Selector = None):
    def s1() -> str:
        table = selector.xpath("//table[@id='tabular-buybox-container']").get()
        if table is None:
            return ""
        table = pandas.read_html(table)
        if len(table) <= 0:
            return ""
        table = table[0].set_index(0)
        if "Ships from" not in table[1]:
            return ""
        s = table[1]["Ships from"]
        return s

    def s2() -> str:
        ship = selector.xpath("normalize-space(//div[@id='sfsb_accordion_head']/div/div/span[2]/text())").get()
        return ship or ""

    def s3() -> str:
        ship_sel = selector.xpath("normalize-space(string(//div[@id='merchant-info']))")
        ship = ship_sel.re("Ships from and sold by (.+).$")
        ship = ship or ship_sel.re("Sold by .+? and Fulfilled by (.+).$")
        if len(ship) > 0:
            return ship[0]
        else:
            return ""

    ship_str = s1() or s2() or s3()
    if ship_str != "":
        p.ship = ship_str.lower()
    else:
        p.ship = None


def parse_delivery(p: Product, selector: parsel.Selector = None):
    delivery = selector.xpath("string(//div[@id='contextualIngressPtLabel_deliveryShortLine'])").get()
    delivery = delivery or selector.xpath("normalize-space(//span[@id='glow-ingress-line2']/text())").get()
    if delivery is None:
        p.delivery = None
        return
    if delivery in ["Select delivery location", "Select your address"]:
        p.delivery = "US"
        return
    if not delivery.startswith("Deliver to"):
        p.delivery = None
        return

    delivery = re.search(r"Deliver to\s(.*)", delivery)
    if delivery is None:
        p.delivery = None
    else:
        p.delivery = delivery.group(1)


def parse_material(p: Product, selector: parsel.Selector = None):
    material = product_overview_feature_div_table(selector, "Material")
    if material == "":
        p.material = None
    else:
        p.material = material


def parse_description(p: Product, selector: parsel.Selector = None):
    texts = selector.xpath("//div[@id='feature-bullets']//li[not(@id)]/span/text()").getall()
    if len(texts) < 1:
        p.description = None
        return

    desc = list()
    for t in texts:
        desc.append(t.strip())
    p.description = desc


def parse_title(p: Product, selector: parsel.Selector = None):
    title = selector.xpath("normalize-space(//span[@id='productTitle']/text())").get()
    p.title = title


def parse_size(p: Product, selector: parsel.Selector = None):
    dimensions = product_details_table(selector, "Product Dimensions")
    dimensions = dimensions or product_details_table(selector, "Package Dimensions")
    if not dimensions.endswith("inches"):
        p.size_length = None
        p.size_width = None
        p.size_height = None
        return

    dimensions = parse_number(dimensions, first=False)
    if len(dimensions) >= 3:
        p.size_length = str(dimensions[0]) + " in"
        p.size_width = str(dimensions[1]) + " in"
        p.size_height = str(dimensions[2]) + " in"
    elif len(dimensions) == 2:
        p.size_length = str(dimensions[0]) + " in"
        p.size_width = str(dimensions[1]) + " in"
        p.size_height = None
    elif len(dimensions) == 1:
        p.size_length = str(dimensions[0]) + " in"
        p.size_width = None
        p.size_height = None
    else:
        p.size_length = None
        p.size_width = None
        p.size_height = None


def parse_color(p: Product, selector: parsel.Selector = None):
    color = selector.xpath("normalize-space(string(//div[@id='prodDetails']/span))").re_first("Color:(.+?)(?: |$)")
    if color is None:
        p.color = None
    else:
        p.color = color.lower()


def parse_variation(p: Product, selector: parsel.Selector = None):
    variation = selector.xpath(
        "normalize-space(//script[contains(text(), 'twister-js-init-dpx-data')]/text())"
    ).re_first("dataToReturn = {.+};")
    if variation is None:
        p.variation_values = None
        p.selected_variations = None
        p.asin_variation_values = None
        return

    try:
        variation = js2py.eval_js(variation)
        labels = variation.variationDisplayLabels.to_dict()
        values = variation.variationValues.to_dict()
        selected = variation.selected_variations.to_dict()
        variations = variation.asinVariationValues.to_dict()
    except (js2py.internals.simplex.JsException, AttributeError):
        p.variation_values = None
        p.selected_variations = None
        p.asin_variation_values = None
        return

    def change_key(d: dict):
        return {labels[k]: v for k, v in d.items() if k in labels}

    def change_variations(vars_ori: dict) -> Dict[str, dict]:
        vars_change = dict()
        for asin, var in vars_ori.items():
            var_change = dict()
            for k, v in var.items():
                if k in labels and k in values:
                    var_change[labels[k]] = values[k][int(v)]
                else:
                    var_change[k] = v
            vars_change[asin] = var_change
        return vars_change

    p.variation_values = change_key(values)
    p.selected_variations = change_key(selected)
    p.asin_variation_values = change_variations(variations)
