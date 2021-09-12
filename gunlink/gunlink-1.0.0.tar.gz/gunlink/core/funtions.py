
import re
import socket
from ipwhois import IPWhois
import numpy as np
from typing import (
    Tuple, Union, Optional)

from .errors import (
    lookupError, tinyUrlError)

from pyshorteners import Shortener


def inbtw_finders(string: str, start: str, end: str) -> Union[str, None]:
    """
    
    :param string: string
    :param start: starting
    :param end: ending
    :return: filtered string
    :rtype: Union[str,None]
    
    """
    try:

        return re.search(f'{start}(.+?){end}', string).group(1)
    except AttributeError:
        return ''


def isurl(url: str) -> bool:
    """
    
    :param url: url
    :return: is URL valid or not
    :rtype: bool
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return True if re.match(regex, url) is not None else False


def protocol(url: str) -> Optional[str]:
    """
    
    :param url: url
    :return: https or http or tcp
    :rtype: Optional[str]
    """
    return inbtw_finders(url, "", "://")


def domain_step(url: str, url_protocol: str) -> str:
    """

    :param url: url
    :param url_protocol: simpler for domain function
    :return: filtered string
    :return: str
    """
    return inbtw_finders(string=url, start=(url_protocol + "://"), end="/")


def domain(url: str, url_protocol: str) -> Tuple[list, str, str, int, str, str]:
    """

    :param url: url
    :param url_protocol: https or http or tcp
    :return: list of sub domain, root domain, top domain, port number, main domain, main domain with protocol
    :rtype :Tuple[list[str], str, str, int, str, str]
    """
    main_domain: str = domain_step(url=url, url_protocol=url_protocol)
    top: str
    root: str
    sub: list
    port: int = -1

    try:
        data: list = main_domain.split(".")
        top = data[-1].split("?")[0]

        root = data[-2]
        sub = data[:-2]
    except:
        top = ''
        temp_local = main_domain.split(":")
        root = temp_local[0]
        sub = []
        port = int(temp_local[1])

    main_domain = f"{root}.{top}"

    return sub, root, top, port, main_domain, f"{url_protocol}://{main_domain}/"


def query_step(string: str, dic: dict) -> Tuple[str, dict]:
    """

    :param string: string
    :param dic: dictionary
    :return:path and query
    :rtype :Tuple[str, dict[str, str]]
    """
    string_list: list[str] = string.split("?")
    temp: list
    path: str = string_list[0]

    try:

        for i in string_list[1].split("&"):
            temp = i.split("=")
            try:
                dic[temp[0]] = temp[1]
            except:
                dic[temp[0]] = ''
    except:
        pass

    return path, dic


def path_query(url: str) -> Tuple[object, dict]:
    """

    :param url: url
    :return: path and query
    :rtype :Tuple[str, dict[str,]]
    """
    data: list[str] = url.split("/")[3:]

    paths: np.ndarray = np.array([])
    query: dict['str', 'str'] = {}

    for i in data:
        p, query = query_step(i, query)
        paths = np.append(paths, p)

    return paths.tolist(), query


def find_ip(main_domain: str) -> str:
    """

    :param main_domain: main_domain
    :return: ip address for the website
    :rtype: str
    """
    try:

        return socket.gethostbyname(main_domain)
    except:
        if 'localhost' in main_domain:
            return socket.gethostbyname(socket.gethostname())
        else:
            return "-1"


def add_backslash(url: str) -> str:
    """

    :param url: url
    :return: add backslash to url
    :rtype: str
    """
    return url if "/" in url[-1] else f"{url}/"


def who_is_info() -> str:
    """

    :return: information about the whois
    :rtype:str
    """
    return """
    {
    'query' (str) - The IP address
    'asn' (str) - The Autonomous System Number
    'asn_date' (str) - The ASN Allocation date
    'asn_registry' (str) - The assigned ASN registry
    'asn_cidr' (str) - The assigned ASN CIDR
    'asn_country_code' (str) - The assigned ASN country code
    'asn_description' (str) - The ASN description
    'nets' (list) - Dictionaries containing network
                    information which consists of the fields listed in the
                    ipwhois.whois.RIR_WHOIS dictionary.
    'raw' (str) - Raw whois results if the inc_raw parameter is True.
    'referral' (dict) - Referral whois information if
                        get_referral is True and the server is not blacklisted.
                        Consists of fields listed in the ipwhois.whois.RWHOIS
                        dictionary.
    'raw_referral' (str) - Raw referral whois results if the inc_raw parameter is True.
    'nir' (dict) - ipwhois.nir.NIRWhois() results if inc_nir is True.
    
    }"""


def whois(ip: str) -> Union[dict, None]:
    """

    :param ip: ip address
    :return: information about that ip address
    :rtype:Union[str,None]
    """

    try:

        return IPWhois(ip).lookup_whois()
    except:
        raise lookupError


def tiny(url: str) -> Union[str, None]:
    """

    :param url: url
    :return: short url
    :rtype: Union[str,None]
    """
    try:
        return Shortener().tinyurl.short(url)
    except:
        raise tinyUrlError
