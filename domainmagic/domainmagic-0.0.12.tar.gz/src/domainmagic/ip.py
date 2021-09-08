# -*- coding: UTF-8 -*-
#   Copyright 2012-2020 Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#

"""ip tools"""

from domainmagic.validators import is_ipv4, is_ipv6
from domainmagic.fileupdate import updatefile
import stat

try:
    import geoip2.database
    PYGEOIP_AVAILABLE = True
except ImportError:
    PYGEOIP_AVAILABLE = False


GEOIP_FILE = '/tmp/GeoLite2-Country.mmdb'
GEOIP_URL = 'https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz'


def ip6_expand(ip):
    """remove :: shortcuts from ip adress - the returned address has 8 parts"""
    # TODO: there's probably a faster way to do this...

    # atm we only support plain ipv6 adresses
    if '.' in ip:
        raise ValueError()
    shortindex = ip.find('::')
    if shortindex < 0:
        return ip
    leading = ip[:shortindex]
    trailing = ip[shortindex + 2:]
    lparts = 0
    tparts = 0
    if leading:
        lparts = len(leading.split(':'))

    if trailing:
        tparts = len(trailing.split(':'))
    missingparts = 8 - lparts - tparts
    parts = ip.split(':')
    replace = ":".join(['0' for i in range(missingparts)])
    ret = ""
    if len(leading) > 0:
        ret += leading + ":"
    ret += replace
    if len(trailing) > 0:
        ret += ":" + trailing
    return ret


def ip_reversed(ip):
    """Return the reversed ip address representation for dns lookups"""
    if is_ipv4(ip):
        octets = ip.split('.')
        octets.reverse()
        return ".".join(octets)
    if is_ipv6(ip):
        expanded = ip6_expand(ip)
        parts = expanded.split(':')
        parts.reverse()
        return '.'.join(parts)

    raise ValueError("invalid ip address: %s" % ip)


def convert_hex_ip(ip):
    ipbytes = ip.split('.')
    newbytes = []
    for ipbyte in ipbytes:
        if ipbyte.startswith('0x'):
            try:
                ipbyte = str(int(ipbyte, 0))
                newbytes.append(ipbyte)
            except ValueError:
                raise ValueError("invalid ip address: %s" % ip)
        else:
            newbytes.append(ipbyte)
    return '.'.join(newbytes)


@updatefile(GEOIP_FILE, GEOIP_URL, refresh_time=24*3600, minimum_size=1000, unpack=True,
            filepermission=stat.S_IWUSR | stat.S_IRUSR | stat.S_IWGRP | stat.S_IRGRP | stat.S_IROTH)
def geoip_country_code_by_addr(ip):
    assert PYGEOIP_AVAILABLE, "geoip2 is not installed"
    gi = geoip2.database.Reader(GEOIP_FILE)
    data = gi.country(ip)
    retval = data.country.iso_code
    if retval is None: # some ips are not assigned to a country, only to a continent (usually EU)
        retval = data.continent.code
    return retval
