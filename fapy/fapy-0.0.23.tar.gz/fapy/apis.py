import json as _json
import urllib.request as _urllib_request


def geoip_ipinfo(ip):
    url = 'https://ipinfo.io/%s/json' % ip
    with _urllib_request.urlopen(url) as response:
        d = _json.loads(response.read().decode())
        if d:
            v = (d.get("country"), d.get("region"), d.get("city"))
            return '%s, %s, %s' % v


def ext_ip_ifconfigme():
    url = 'https://ifconfig.me'
    with _urllib_request.urlopen(url) as response:
        return response.read().decode().strip()
