import xml.etree.ElementTree as ETree
from copy import copy as _copy

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence


MODIFY_METHODS = {"append": list.append, "insert": list.insert, "pop": list.pop}


def process_modify_xml(xml, data):
    if isinstance(data, MutableSequence):
        return process_mseqmodify_xml(xml, data)


def _handle_append(tree, copy):
    method = MODIFY_METHODS["append"]
    for element in tree.iter("append"):
        items = filter(lambda x: x.tag == "item", element)

        for item in items:
            if item.attrib.get("ensure_str") == "True":
                item = str(item.attrib["item"])
            else:
                item = eval(item.attrib["item"])

            method(copy, item)


def _handle_insert(tree, copy):
    method = MODIFY_METHODS["insert"]
    for element in tree.iter("insert"):
        items = filter(lambda x: x.tag == "item", element)

        for item in items:
            if item.attrib.get("ensure_str") == "True":
                item, location = str(item.attrib["item"]), int(item.attrib["location"])
            else:
                item, location = eval(item.attrib["item"]), int(item.attrib["location"])

            method(copy, location, item)

    return copy


def _handle_pop(tree, copy):
    method = MODIFY_METHODS["pop"]
    for element in tree.iter("popitem"):
        items = filter(lambda x: x.tag == "item", element)

        for item in items:
            if item.attrib.get("ensure_str") == "True":
                location = int(item.attrib["location"])
            else:
                location = int(item.attrib["location"])

            method(copy, location)


def process_mseqmodify_xml(xml, data):
    copy = _copy(data)
    tree = ETree.fromstring(xml)

    _handle_append(tree, copy)
    _handle_insert(tree, copy)
    _handle_pop(tree, copy)

    return copy
