import logging
import os
from platform import system
import requests
import socket

try:
    import cookielib
except ImportError:
    # python 3
    import http.cookiejar as cookielib

_auth_provider = None
_headers = {'Accept-Language': 'en'}

try:
    if system() == 'Windows':
        from requests_negotiate_sspi import HttpNegotiateAuth
        _auth_provider = HttpNegotiateAuth
    else:
        from requests_kerberos import HTTPKerberosAuth, OPTIONAL
        _auth_provider = HTTPKerberosAuth
except ImportError:
    pass

# The initial URL that starts the authentication process.
_IDP_ENTRY_URL = 'https://{}/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp={}'

def is_ipv4(s):
    # Feel free to improve this: https://stackoverflow.com/questions/11827961/checking-for-ip-addresses
    return ':' not in s

dns_cache = {}

def add_custom_dns(domain, port, ip):
    key = (domain, port)
    # Strange parameters explained at:
    # https://docs.python.org/2/library/socket.html#socket.getaddrinfo
    # Values were taken from the output of `socket.getaddrinfo(...)`
    if is_ipv4(ip):
        value = (socket.AddressFamily.AF_INET, 0, 0, '', (ip, port))
    else: # ipv6
        value = (socket.AddressFamily.AF_INET6, 0, 0, '', (ip, port, 0, 0))
    dns_cache[key] = [value]

prv_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args):
    # Uncomment to see what calls to `getaddrinfo` look like.
    #print(args)
    try:
        return dns_cache[args[:2]] # hostname and port
    except KeyError:
        return prv_getaddrinfo(*args)

def fetch_html_encoded_roles(
        adfs_host,
        adfs_cookie_location,
        ssl_verification_enabled,
        provider_id,
        #extranet_ip,
        company_domain,
        adfs_ca_bundle=None,
        username=None,
        password=None,
        sspi=None,
        u2f_trigger_default=None,
):

    # Support for Kerberos SSO on Windows via requests_negotiate_sspi
    # also requires tricking the server into thinking we're using IEq
    # so that it servers up a redirect to the IWA page.
    if sspi:
        _headers['User-Agent'] = 'HCS/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
                                 #'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/60.0'

    _headers['Host'] = adfs_host
    session = requests.Session()
    # Redirect example.com to the IP of test.domain.com (completely unrelated).
    #add_custom_dns(adfs_host, 443, extranet_ip)
    #socket.getaddrinfo = new_getaddrinfo

    # LWPCookieJar has an issue on Windows when cookies have an 'expires' date too far in the future and they are converted from timestamp to datetime.
    # MozillaCookieJar works because it does not convert the timestamps.
    # Duo uses 253402300799 for its cookies which translates into 9999-12-31T23:59:59Z.
    # Windows 64bit maximum date is 3000-12-31T23:59:59Z, and 32bit is 2038-01-18T23:59:59Z.
    session.cookies = cookielib.MozillaCookieJar(filename=adfs_cookie_location)

    try:
        have_creds = (username and password) or (_auth_provider and sspi)
        session.cookies.load(ignore_discard=not(have_creds))
    except IOError as e:
        error_message = getattr(e, 'message', e)
        logging.debug(
            u'Attempt to load authentication cookies into session failed. '
            u'Re-authentication will be performed. '
            u'The error: {}'.format(error_message)
        )

    if _auth_provider and sspi:
        domain = None
        if username:
            if '@' in username: # User principal name (UPN) format
                username, domain = username.split('@', 1)
            elif '\\' in username: # Down-level logon name format
                domain, username = username.split('\\', 1)
            else:
                domain=company_domain
        if system() == 'Windows':
            auth = _auth_provider(username, password, domain)
        elif username and domain:
            auth = _auth_provider(principal="{}@{}".format(username, domain), mutual_authentication=OPTIONAL)
        else:
            auth = _auth_provider(mutual_authentication=OPTIONAL)
        data = None
    else:
        auth = None
        if username:
            if '@' not in username: # User principal name (UPN) format
                username = username + '@' + company_domain
        data={
            'UserName': username,
            'Password': password,
            'AuthMethod': 'FormsAuthentication'
        }
    if adfs_ca_bundle:
        ssl_verification = adfs_ca_bundle
    else:
        ssl_verification = ssl_verification_enabled

    # Opens the initial AD FS URL and follows all of the HTTP302 redirects
    authentication_url = _IDP_ENTRY_URL.format(adfs_host, provider_id)
    # print('Authtication URL {} , headers {}, ip {}'.format(authentication_url, _headers.items(), extranet_ip))
    response = session.post(
        authentication_url,
        verify=ssl_verification,
        headers=_headers,
        auth=auth,
        data=data
    )

    logging.debug(u'''Request:
        * url: {}
        * headers: {}
    Response:
        * status: {}
        * headers: {}
        * body: {}
    '''.format(
            authentication_url,
            response.request.headers,
            response.status_code,
            response.headers,
            response.text
       ))

    if response.status_code >= 400:
        session.cookies.clear()

    mask = os.umask(0o177)
    try:
        session.cookies.save(ignore_discard=True)
    finally:
        os.umask(mask)

    del auth
    del data
    del username
    password = '###################################################'
    del password

    # Decode the response
    return response, session
