
from ciopath.gpath_list import PathList
import importlib


__data__ = None


def data(node):
    global __data__

    if __data__:
        return __data__

    scrapers = []
    attr = node.attr("assetScrapers")
    for attr_element in attr:
        if not attr_element.attr("assetScraperActive").get():
            continue
        script = attr_element.attr("assetScraperName").get().strip()
        if not script:
            continue
        scrapers.append(script)

    result = []
    for script in scrapers:
        scraper_module = importlib.import_module(script)
        try:
            reload(scraper_module)
        except:
            importlib.reload(scraper_module)
        paths = scraper_module.run(node)
        result += [p["path"] for p in paths if p["path"].strip()]

    result += [p for p in list(node.attr("extraAssets").get()) if p]

    __data__ = PathList(*result)

    return __data__


def clear():
    global __data__
    __data__ = None
