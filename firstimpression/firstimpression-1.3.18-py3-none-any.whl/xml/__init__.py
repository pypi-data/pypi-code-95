from firstimpression.api.request import request
from firstimpression.scala import Log
import xml.etree.ElementTree as ET


def get_xml(url):
    response, is_error = request(url)
    if is_error:
        if response['type'] == 'ERROR':
            Log('ERROR', 'get_feed').log('request {} -> {}'.format(response['reason'], response['message']))
        elif response['type'] == 'WARN':
            Log('WARN', 'get_feed').log('request {} -> {}'.format(response['reason'], response['message']))
        exit()
    return ET.fromstring(response.content)


def get_text_from_element(element, tag_name):
    return element.find(tag_name).text


def get_items_from_element(element, tag_name):
    return element.findall(tag_name)


def get_attrib_from_element(element, tag_name, attrib_name):
    return element.find(tag_name).attrib[attrib_name]
