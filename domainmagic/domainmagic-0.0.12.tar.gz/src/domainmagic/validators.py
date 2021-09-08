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
"""Validators"""
import re
from urllib.parse import urlparse


REGEX_IPV4 = """(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"""
HEXREGEX_IPV4 = """(?:0x[0-9a-f]{1,2})\.(?:0x[0-9a-f]{1,2})\.(?:0x[0-9a-f]{1,2})\.(?:0x[0-9a-f]{1,2})"""

REGEX_CIDRV4 = REGEX_IPV4 + """\/(?:[012]?[0-9]|3[0-2])"""

# from http://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
# with added dot escapes and removed capture groups
REGEX_IPV6 = """(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"""

REGEX_CIDRV6 = REGEX_IPV6 + """\/(?:12[0-8]|1[01][0-9]|[1-9]?[0-9])"""

# read doc and explanations in is_hostname
REGEX_HOSTNAME = """([_a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?)?(\.([_a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?))*(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*"""

REGEX_EMAIL_LHS = """[a-zA-Z0-9!#$%&'*+/=?^_`{|}~@-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"""

URI_SCHEMES = ['http', 'https', 'ftp']


def _apply_rgx(rgx, content):
    if not isinstance(content, str):
        return False
    return re.match("^%s$" % rgx, content) is not None



def is_ipv4(content):
    """Returns True if content is a valid IPv4 address, False otherwise"""
    return _apply_rgx(REGEX_IPV4, content) or _apply_rgx(HEXREGEX_IPV4, content)


def is_cidrv4(content):
    """Returns True if content is a valid IPv4 CIDR, False otherwise"""
    return _apply_rgx(REGEX_CIDRV4, content)


def is_ipv6(content):
    """Returns True if content is a valid IPv6 address, False otherwise"""
    return _apply_rgx(REGEX_IPV6, content)


def is_cidrv6(content):
    """Returns True if content is a valid IPv6 CIDR, False otherwise"""
    return _apply_rgx(REGEX_CIDRV6, content)


def is_ip(content):
    """Returns True if content is a valid IPV4 or IPv6 address, False otherwise"""
    return is_ipv4(content) or is_ipv6(content)


def is_hostname(content, check_valid_tld=False, check_resolvable=False):
    """
    Returns True if content is a valid hostname (but not necessarily a FQDN)
    
    a hostname label may start with underscore but cannot have an underscore at a later position
    a hostname label may contain dashes but not as first or last character
    a hostname label may only contain latin letters a-z, decimal numbers, dashes and underscore
    a hostname label must contain at least one character
    a hostname label must not exceed 63 characters
    a hostname should not exceed 255 characters (not covered by regex)
    more complex rules apply to FQDNs which are not covered by regex
    IDN is not covered by regex. convert to punycode first: u'idn-höstnäme.com'.encode('idna')
    
    :param content: the hostname to check
    :param check_valid_tld: set to True to only accept FQDNs with valid IANA approved TLD
    :param check_resolvable: set to True to only accept hostnames which can be resolved by DNS
    :return: True if valid hostname, False otherwise
    """
    if not isinstance(content, str):
        return False
    
    if len(content) > 255 or not _apply_rgx(REGEX_HOSTNAME, content):
        return False
    
    if check_valid_tld:
        from domainmagic.tld import get_default_tldmagic
        if get_default_tldmagic().get_tld(content) is None:
            return False
    
    if check_resolvable:
        from domainmagic.dnslookup import DNSLookup
        dns = DNSLookup()
        for qtype in ['A', 'AAAA', 'MX', 'NS', 'SOA', 'SRV', 'TXT']:
            result = dns.lookup(content, qtype)
            if len(result)>0:
                break
        else:
            return False
    
    return True


def is_fqdn(content, check_valid_tld=False, check_resolvable=False):
    """
    Returns True if content is a valid FQDN
    
    Difference hostname vs FQDN:
    a hostname consists of at least one valid label
    a FQDN consist of at least two valid labels, thus contains a .
    
    :param content: the FQDN to check
    :param check_valid_tld: set to True to only accept FQDNs with valid IANA approved TLD
    :param check_resolvable: set to True to only accept FQDNs which can be resolved by DNS
    :return: True if valid FQDN, False otherwise
    """
    if not isinstance(content, str):
        return False
    
    if not '.' in content.strip('.'):
        return False
        
    if not is_hostname(content, check_valid_tld, check_resolvable):
        return False
    
    return True


def is_email(content, check_valid_tld=False, check_resolvable=False):
    """
    Returns True if content is a valid email address
    :param content: the email address to check
    :param check_valid_tld: set to True to only accept FQDNs with valid IANA approved TLD
    :param check_resolvable: set to True to only accept FQDNs which can be resolved by DNS
    :return: True if valid email address, False otherwise
    """
    if not isinstance(content, str):
        return False
    
    if not '@' in content:
        return False
    
    lhs, domain = content.rsplit('@', 1)
    
    if not _apply_rgx(REGEX_EMAIL_LHS, lhs):
        return False
    
    if not is_fqdn(domain, check_valid_tld, check_resolvable):
        return False
    
    return True


def is_url(content):
    try:
        parsed = urlparse(content)
        if parsed.scheme and parsed.netloc and parsed.scheme in URI_SCHEMES:
            return True
        else:
            return False
    except Exception:
        return False


def is_url_tldcheck(content, exclude_fqdn=(), exclude_domain=()):
    """Check if it's a valid url by checking tld"""
    from .tld import get_default_tldmagic
    from .extractor import is_ip, domain_from_uri

    if not content:
        return False

    tldmagic = get_default_tldmagic()

    try:
        fqdn = domain_from_uri(content)
        if fqdn in exclude_fqdn:
            return False
    except Exception:
        # log error
        return False

    try:
        domain = tldmagic.get_domain(fqdn)
    except Exception:
        return False

    if domain in exclude_domain:
        return False

    # ip doen't have tld, but url is still valid
    isip = is_ip(domain)
    has_tld = tldmagic.get_tld(domain) if domain else ""

    # either it's an ip or there has to be domain & tld
    is_valid = (bool(domain) and bool(has_tld)) or bool(isip)
    return is_valid
