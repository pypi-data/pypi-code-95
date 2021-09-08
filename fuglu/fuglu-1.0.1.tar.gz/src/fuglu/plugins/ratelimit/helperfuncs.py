import logging
import typing as tp
import ipaddress as ia
import ipaddress
from domainmagic import extractor, tld
from domainmagic.validators import is_url_tldcheck
from fuglu.extensions import dnsquery
from fuglu.stringencode import force_uString
from fuglu.shared import Suspect

BE_VERBOSE = False # for debugging


def ip2network(ipstring: str, prefixlen: int=32) -> str:
    """
    Take an ip string and the prefixlen to calculate the network string
    which can be used as a key in the RateLimitPlugin
    """
    return ia.ip_network(f"{ipstring}/{prefixlen}", False).with_prefixlen


# Singleton implementation for Domainmagic
class DomainMagic(object):
    _instance = None
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.tldmagic = tld.TLDMagic()


def get_domain_from_uri(uri: str, suspect=None) -> tp.Optional[str]:
    """Extract domain from uri"""
    exclude_fqdn = ['www.w3.org', 'schemas.microsoft.com']
    exclude_domain = ['avast.com']

    if not uri:
        return None

    suspectid = suspect.id if suspect else '<>'
    try:
        fqdn = extractor.domain_from_uri(uri)
        if fqdn in exclude_fqdn:
            return None
    except Exception as e:
        # log error
        logging.getLogger('fuglu.ratelimit.helperfuncs.get_domain_from_uri').error(f"{suspectid} msg: {str(e)} uri: {uri}")
        return None

    try:
        domain = DomainMagic.instance().tldmagic.get_domain(fqdn)
    except Exception as e:
        # log error
        logging.getLogger('fuglu.ratelimit.helperfuncs.get_domain_from_uri').error(f"{suspectid} msg: {str(e)} fqdn: {fqdn}")
        return None

    if domain in exclude_domain:
        return None
    return domain


def split_helo2host_domain(helo: str, suspect=None):
    """Split helo to host, domain"""
    domain = get_domain_from_uri(helo, suspect=suspect)
    suspectid = suspect.id if suspect else '<>'
    if not domain:
        return helo, ""
    try:
        hostname = helo.rsplit("."+domain, 1)[0]
    except Exception as e:
        logging.getLogger('fuglu.ratelimit.helperfuncs.split_helo2host')\
            .error(f"{suspectid} msg: {str(e)} helo: {helo}, domain: {domain}")
        hostname = ""
    return hostname, domain


# Singleton implementation for GeoIP
class GeoIP(object):
    _instances = {}

    @classmethod
    def instance(cls, filename):
        try:
            return cls._instances[filename]
        except KeyError:
            newinstance = cls(filename)
            cls._instances[filename] = newinstance
            return newinstance

    def __init__(self, filename):
        try:
            from geoip2.database import Reader
        except ImportError:
            Reader = None

        self._filename = filename
        self._reader = Reader(filename) if Reader else None

    def print(self):
        print(f'filename is(id={id(self)}): {self._filename}')

    @property
    def reader(self):
        return self._reader


def asn(ipaddress: tp.Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address], geoipfilename: str)\
        -> tp.Tuple[int, str, tp.Union[str], tp.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    """Extract ASN properties

    geoipfilename is geoip filename containing as ndata
    """
    from geoip2.errors import AddressNotFoundError
    try:
        response = GeoIP.instance(geoipfilename).reader.asn(ipaddress)
    except AddressNotFoundError:
        return None

    try:
        response_network = response.network
    except AttributeError:
        # older geoip versions
        response_network = None

    return (
        response.autonomous_system_number,
        response.autonomous_system_organization,
        response.ip_address,
        response_network,
    )

def match_key_in_array(inputarray: tp.Optional[tp.List[str]], searchstring: str = "", suspect=None) -> tp.Optional[str]:
    """Search for string in array"""
    if inputarray is None:
        return None

    suspectid = suspect.id if suspect else '<>'
    foundaddr = None
    if inputarray and searchstring in inputarray:
        foundaddr = searchstring

    if BE_VERBOSE:
        logging.getLogger('fuglu.ratelimit.helperfuncs.match_key_in_array') \
            .debug(f"{suspectid} found {foundaddr} in {inputarray}")

    # don't return an empty list, return None in this case
    return foundaddr if foundaddr else None


def valid_fqdn(urilist: tp.Optional[tp.List[str]], suspect=None) -> tp.Optional[tp.List[str]]:
    """Reduce uri list to fqdn's only"""
    if urilist is None:
        return None
    suspectid = suspect.id if suspect else '<>'
    domains = set()
    for url in urilist:
        try:
            if url and is_url_tldcheck(url,
                                       exclude_fqdn=['www.w3.org', 'schemas.microsoft.com'],
                                       exclude_domain=['avast.com']
                                       ):
                domains.add(extractor.fqdn_from_uri(url))
        except Exception as e:
            logging.getLogger('fuglu.ratelimit.helperfuncs.match_key_in_array')\
                .error(f"{suspectid} (examine:fqdn_from_uri): {e} for uri: {url}")
    domains = list(domains)
    # don't return an empty list, return None in this case
    return domains if domains else None


def convert_truefalse(input: tp.Optional[str], suspect=None) -> str:
    """Split helo to host, domain"""
    return str(bool(input))


def create_sudomain_list(domain: str, reverse: bool=False, suspect=None) -> tp.Optional[tp.List[str]]:
    """
    Create subdomain list, from domain to smallest subdomain
    unless reversed.

    Example:
        - in: a.b.c.d.com
          out: [d.com, c.d.com, b.c.d.com, a.b.c.d.com]
        - in: a.b.c.d.com (reverse=True)
          out: [a.b.c.d.com, b.c.d.com, c.d.com, d.com]
    """

    suspectid = suspect.id if suspect else '<>'

    try:
        tldcount = DomainMagic.instance().tldmagic.get_tld_count(domain)
    except Exception as e:
        # log error
        logging.getLogger('fuglu.ratelimit.helperfuncs.create_subdomain_list').error(f"{suspectid} msg: {str(e)} domain: {domain}")
        return None

    parts = domain.split('.')

    subrange = range(tldcount + 1, len(parts) + 1)
    checkstrings = []
    for subindex in subrange:
        subdomain = '.'.join(parts[-subindex:])
        checkstrings.append(subdomain)
    if checkstrings and reverse:
        checkstrings = checkstrings[::-1]
    return checkstrings


def packargs(*args, **kwargs):
    """
    Small helper function if result should be packed
    This is required if output of the previous function is an array
    and it should be passed as an array into the next function, because
    usually arrays are expanded and threated as separate arguments into
    the next function
    """
    if args:
        return (args,)
    else:
        return None


def get_nameservers(idomain: tp.Union[str, tp.List[str]], suspect=None) -> tp.Optional[tp.List[str]]:
    """For input domain/list of domains return first set of nameservers found"""
    suspectid = suspect.id if suspect else '<>'
    if isinstance(idomain, str):
        dlist = [idomain]
    else:
        dlist = idomain

    # check if list is nonempty
    if dlist and isinstance(dlist, (list, tuple)):
        for dom in dlist:
            try:
                answers: tp.List[str] = dnsquery.lookup(dom, dnsquery.QTYPE_NS)
                answers = [a.rstrip('.') for a in answers if a and a.rstrip('.')] if answers else []
                if len(answers):
                    return answers
            except Exception as e:
                logger = logging.getLogger('fuglu.ratelimit.helperfuncs.create_subdomain_list')
                logger.error(f"{suspectid} got: {str(e)} querying ns for: {dom}")

    return None

def filter4left_tuple(tuplelist: tp.Union[tp.Tuple, tp.List],
                      filter: str,
                      lowercase: bool = True,
                      suspect=None) -> tp.Optional[tp.List[str]]:
    suspectid = suspect.id if suspect else '<>'
    if isinstance(tuplelist, tuple):
        tuplelist = tuplelist[0]
    newlist = []
    for tup in tuplelist:
        k, v = tup
        k = force_uString(k, convert_none=True)
        if lowercase:
            k = k.lower()
        if k == filter:
            newlist.append(v)
    if newlist:
        return newlist
    else:
        return None


def arraylength_largerthan(array: tp.List, maxlength=0, suspect=None) -> bool:
    suspectid = suspect.id if suspect else '<>'
    islarger = len(array) > maxlength
    if suspect:
        # set tags so values can be used in reject message
        try:
            # note: these tags will be prefixed by "tag_" if used in the reject message,
            # Example: "array length exceeded ${tag_arraylength} > ${tag_maxlength}"
            suspect.tags["arraylength"] = len(array)
            suspect.tags["maxlength"] = maxlength
        except Exception as e:
            logging.getLogger('fuglu.ratelimit.helperfuncs.arraylength_largerthan')\
                .debug(f"Problem setting tags: {str(e)}")
    logging.getLogger('fuglu.ratelimit.helperfuncs.arraylength_largerthan')\
        .debug(f"{suspectid} arraylength: {len(array)} {'>' if islarger else '<='} {maxlength}")
    return islarger


def decode_from_type_headers(tuplelist: tp.Union[tp.Tuple, tp.List], name="From", suspect=None) -> tp.Optional[tp.List[str]]:
    suspectid = suspect.id if suspect else '<>'
    if isinstance(tuplelist, tuple):
        tuplelist = tuplelist[0]

    buffer = b"\r\n".join([tup[0]+b": "+tup[1] for tup in tuplelist])
    if buffer:
        # build dummy suspect
        s = Suspect("from@fuglu.org", "to@fuglu.org", tempfile=None, inbuffer=buffer)
        addrs = s.parse_from_type_header(header=name, validate_mail=True)
        if addrs:
            return (addrs, )
        else:
            return None
    else:
        return None


def select_tuple_index(tuplelist: tp.Union[tp.Tuple, tp.List],
                 index: int,
                 suspect=None) -> tp.Optional[tp.List[str]]:
    suspectid = suspect.id if suspect else '<>'
    if isinstance(tuplelist, tuple):
        tuplelist = tuplelist[0]
    try:
        return ([tup[index] for tup in tuplelist], )
    except Exception:
        return None


def domain_from_email(emaillist: tp.List[str], suspect=None) -> tp.Optional[tp.List[str]]:
    if emaillist:
        out = list(set([m.rsplit("@", 1)[1] for m in emaillist if m and "@" in m]))
        if out:
            return out
    return None
