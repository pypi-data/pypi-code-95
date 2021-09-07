from firstimpression.api.request import request
from firstimpression.scala import Log
import xml.etree.ElementTree as ET


def get_feed(url):
    response, is_error = request(url)
    if is_error:
        if response['type'] == 'ERROR':
            Log('ERROR', 'get_feed').log('request {} -> {}'.format(response['reason'], response['message']))
        elif response['type'] == 'WARN':
            Log('WARN', 'get_feed').log('request {} -> {}'.format(response['reason'], response['message']))
        exit()
    return ET.fromstring(response.content)
