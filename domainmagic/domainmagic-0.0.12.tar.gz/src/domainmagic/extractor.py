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
import re
import os
import time
import logging
from domainmagic.tld import get_IANA_TLD_list
from domainmagic.validators import REGEX_IPV4, REGEX_IPV6, is_hostname, is_ip, is_url, HEXREGEX_IPV4
import traceback
import io
from urllib import parse as urlparse
from html import unescape as html_unescape

    
EMAIL_HACKS = {
    '@' : ['(at)', ' (at) ', ' AT ', '[at]', ' @ '],
    '.' : ['(dot)', ' (dot) ', ' DOT ', '[dot]', ' . '],
}


def build_search_re(tldlist=None):
    if tldlist is None:
        tldlist = get_IANA_TLD_list()

    # lookbehind to check for start of url
    # start with
    # - start of string
    # - whitespace
    # - " for href
    # - ' for borked href
    # - = borked href without " or '
    # - > for links in tags
    # - () after opening or closing parentheses (seen in chinese spam)
    # - * seen in spam
    # - - seen in spam (careful, legit character in hostname)
    # - [ for links in square brackets (seen in spam)
    # - allow ":" in front of link if not followed by //, for example "confuse:www.domain.invalid"
    reg = r"(?:(?<=^)|(?<="
    reg += r"(?:\s|[\"'=\<\>\(\)\*\[]|:(?!\/\/))"
    reg += r"))"

    # url starts here
    reg += r"(?:"
    reg += r"(?:https?://|ftp://)"  # protocol
    reg += r"(?:[a-z0-9!%_$.\-]+(?::[a-z0-9!%_$.\-]+)?@)?"  # username/pw
    reg += r")?"

    # domain
    reg += r"(?:"  # domain types

    # standard domain
    allowed_hostname_chars = r"-a-z0-9_"
    reg += r"[a-z0-9_]"  # first char can't be a hyphen
    reg += r"[" + allowed_hostname_chars + \
        r"]*"  # there are domains with only one character, like 'x.org'
    reg += r"(?:\.[" + allowed_hostname_chars + \
        r"]+)*"  # more hostname parts separated by dot
    reg += r"\."  # dot between hostname and tld
    reg += r"(?:"  # tldgroup
    reg += r"|".join([x.replace('.', r'\.') for x in tldlist])
    reg += r")\.?"  # standard domain can end with a dot

    # dotquad
    reg += r"|%s" % REGEX_IPV4
    reg += r"|%s" % HEXREGEX_IPV4

    # ip6
    reg += r"|\[%s\]" % REGEX_IPV6

    reg += r")"  # end of domain types

    # optional port
    reg += r"(?:\:\d{1,5})?"

    # after the domain, there must be a path sep or quotes space or ?
    # or > (for borked href without " or ') end,
    # or ] (for domain-only uri in square brackets')
    # or < (for uri enclosed in html tag)
    # or ) (for uri enclosed in parenthesis)
    # check with lookahead
    reg += r"""(?=[<>\"'/?\]\[)]|\s|$)"""

    # path
    allowed_path_chars = r"-a-z0-9._/%#\[\]~*"
    reg += r"(?:\/[" + allowed_path_chars + r"]+)*"

    # request params
    allowed_param_chars = r"-a-z0-9;._/\![\]?#+%&=@*,:!"
    reg += r"(?:\/?)"  # end domain with optional  slash
    reg += r"(?:\?[" + allowed_param_chars + \
        r"]*)?"  # params must follow after a question mark

    #print(f"RE: {reg}")
    return re.compile(reg, re.IGNORECASE)


def build_email_re(tldlist=None):
    if tldlist is None:
        tldlist = get_IANA_TLD_list()

    reg = r"(?=.{0,64}\@)"                         # limit userpart to 64 chars
    reg += r"(?<![a-z0-9!#$%&'*+\/=?^_`{|}~-])"     # start boundary
    reg += r"("                                             # capture email
    reg += r"[a-z0-9!#$%&'*+\/=?^_`{|}~-]+"         # no dot in beginning
    reg += r"(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*"  # no consecutive dots, no ending dot
    reg += r"\@"
    reg += r"[-a-z0-9._]+\."  # hostname
    reg += r"(?:"  # tldgroup
    reg += r"|".join([x.replace('.', '\.') for x in tldlist])
    reg += r")"
    reg += r")(?!(?:[a-z0-9-]|\.[a-z0-9]))"          # make sure domain ends here
    return re.compile(reg, re.IGNORECASE)


def domain_from_uri(uri):
    """backwards compatibilty name"""
    return fqdn_from_uri(uri)


def fqdn_from_uri(uri):
    """extract the domain(fqdn) from uri"""
    if '://' not in uri:
        uri = "http://" + uri
    fqdn = urlparse.urlparse(uri.lower()).netloc

    #remove user/pass:
    if '@' in fqdn:
        fqdn = fqdn.rsplit('@')[-1]

    # remove port
    portmatch = re.search(':\d{1,5}$', fqdn)
    if portmatch is not None:
        fqdn = fqdn[:portmatch.span()[0]]

    # remove square brackets from ipv6
    fqdn = fqdn.strip('[]')

    return fqdn


def redirect_from_google(uri):
    """backwards compatibilty name"""
    return redirect_from_url(uri)
    
def redirect_from_url(uri, silent=True):
    """extract target domain from cloaking redirection services"""
    try:
        parsed = urlparse.urlparse(html_unescape(uri))
        if  ('google.' in parsed.netloc and parsed.path == '/url') or \
            ('safelinks.protection.outlook.com' in parsed.netloc and parsed.path == '/') or \
            ('yandex.' in parsed.netloc and parsed.path == '/redirect') :
            values = urlparse.parse_qs(parsed.query)
            for key in ['url', 'q']:
                uris = [u for u in values.get(key, []) if is_url(u)]
                if len(uris) > 0:
                    uri = uris[0] # we expect exactly one redirect
    except Exception:
        if not silent:
            raise
    return uri


def direct_param_url(uri, silent=True, use_hacks=0):
    """check for unencoded urls in parameter list"""

    # search keys in parameter list
    skeys = ["https://", "http://"]

    try:
        parsed = urlparse.urlparse(html_unescape(uri))
        values = urlparse.parse_qs(parsed.query)
        if use_hacks == 1 and parsed.query and not any(k in parsed.query for k in skeys):
            return uri

        for pname, plist in values.items():
            for key in ["https://", "http://"]:
                for pval in plist:
                    if key in pval:
                        # return first hit
                        return pval[pval.find(key):]
    except Exception:
        if not silent:
            raise
    return uri

def normalise_blogspot_fqdn(fqdn):
    sp = fqdn.split('.')
    if 'blogspot' in sp:
        idx = sp.index('blogspot')
        dom = sp[:idx+1]
        dom.append('com')
        fqdn = '.'.join(dom)
    return fqdn
    
def normalise_blogspot_uri(uri):
    try:
        parsed = urlparse.urlparse(uri)
        if '.blogspot.' in parsed.netloc:
            fqdn = normalise_blogspot_fqdn(parsed.netloc)
            parsed = parsed._replace(netloc=fqdn)
            parsed = parsed._replace(scheme='https')
            uri = parsed.geturl()
    except Exception:
        pass
    return uri
        


class URIExtractor(object):

    """Extract URIs"""

    def __init__(self, tldlist=None):
        self.tldlist = tldlist
        self.lastreload = time.time()
        self.lastreloademail = time.time()
        self.logger = logging.getLogger('%s.uriextractor' % __package__)
        self.searchre = build_search_re(self.tldlist)
        self.emailre = build_email_re(self.tldlist)
        self.skiplist = set()
        self.maxregexage = 86400  # rebuild search regex once a day so we get new tlds
    
    
    def set_tld_list(self, tldlist):
        """override the tldlist and rebuild the search regex"""
        self.tldlist = tldlist
        self.searchre = build_search_re(tldlist)
        self.emailre = build_email_re(tldlist)
    
    
    def load_skiplist(self, filename: str):
        self.skiplist = self._load_single_file(filename)
    
    
    def _load_single_file(self, filename:str) -> set:
        """return lowercased set of unique entries"""
        if not os.path.exists(filename):
            self.logger.error("File %s not found - skipping" % filename)
            return set()
        with io.open(filename, 'r') as f:
            content = f.read().lower()
        entries = content.split()
        del content
        return set(entries)
    
    
    def _uri_filter(self, uri, use_hacks=False):
        skip = False
        newuri = None
        try:
            domain = fqdn_from_uri(uri.lower())
        except Exception:
            skip = True
            domain = None

        # work around extractor bugs - these could probably also be fixed in the search regex
        # but for now it's easier to just throw them out
        if not skip and domain and '..' in domain:  # two dots in domain
            skip = True

        if not skip and not (is_hostname(domain) or is_ip(domain)):
            skip = True

        if not skip and use_hacks:
            newuri = redirect_from_url(uri)
            newuri = normalise_blogspot_uri(newuri)
            newuri = direct_param_url(newuri, use_hacks=use_hacks) # type: str

        if not skip:
            for skipentry in self.skiplist:
                if domain == skipentry or domain.endswith(".%s" % skipentry):
                    skip = True
                    break

        # axb: trailing dots are probably not part of the uri
        if uri.endswith('.'):
            uri = uri[:-1]
        # also check new uri to prevent a loop with the same uri
        if newuri and newuri.endswith('.'):
            newuri = newuri[:-1]

        return skip, uri, newuri
    
    
    def extracturis(self, plaintext, use_hacks=0):

        # convert use_hacks to integer level
        if not isinstance(use_hacks, int):
            use_hacks = 1 if use_hacks else 0

        if self.tldlist is None and time.time() - self.lastreload > self.maxregexage:
            self.lastreload = time.time()
            self.logger.debug("Rebuilding search regex with latest TLDs")
            try:
                self.searchre = build_search_re()
            except Exception:
                self.logger.error(
                    "Rebuilding search re failed: %s" %
                    traceback.format_exc())

        uris = []
        uris.extend(re.findall(self.searchre, plaintext))

        finaluris = []
        # check skiplist and apply recursive extraction hacks
        for newuri in uris:
            counter = 0
            while newuri is not None and counter < 100:
                # use a counter to be sure we never end up
                # in an infinite loop
                counter += 1

                skip, uri, newuri = self._uri_filter(newuri, use_hacks)
                skipnew = skip
                
                # skip partial uris and uri fragments due to parsing/extraction errors
                for finaluri in finaluris:
                    if uri in finaluri:
                        skip = True
                
                if not skip:
                    finaluris.append(uri)

                if newuri != uri and newuri is not None and not skipnew:
                    finaluris.append(newuri)

                if skipnew or newuri == uri:
                    # don't continue if skipenew is True
                    newuri = None

        # remove left-alone trailing square bracket
        cleaneduris = []
        for furi in finaluris:
            if furi.endswith("]"):
                countleft = furi.count("[")
                countright = furi.count("]")
                if countleft < countright and len(furi) > 1:
                    cleaneduris.append(furi[:-1])
                    continue
            cleaneduris.append(furi)
        return sorted(set(cleaneduris))
    
    
    def extractemails(self, plaintext, use_hacks=0):
        if time.time() - self.lastreloademail > self.maxregexage:
            self.lastreloademail = time.time()
            self.logger.debug("Rebuilding search regex with latest TLDs")
            try:
                self.emailre = build_email_re()
            except Exception:
                self.logger.error(
                    "Rebuilding email search re failed: %s" %
                    traceback.format_exc())
        
        if use_hacks:
            for key in EMAIL_HACKS:
                for value in EMAIL_HACKS[key]:
                    plaintext = plaintext.replace(value, key)
        
        emails = []
        emails.extend(re.findall(self.emailre, plaintext))
        return sorted(set(emails))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    extractor = URIExtractor()
    # logging.info(extractor.extracturis("hello http://www.wgwh.ch/?doener lol
    # yolo.com . blubb.com."))

    # logging.info(extractor.extractemails("blah a@b.com someguy@gmail.com"))

    txt = """
    hello 
    http://bla.com 
    please click on <a href="www.co.uk">slashdot.org/?a=c&f=m</a> 
    or on <a href=www.withoutquotes.co.uk>slashdot.withoutquotes.org/?a=c&f=m</a>   
    www.skipme.com www.skipmenot.com/ x.co/4to2S http://allinsurancematters.net/lurchwont/ muahahaha x.org
    dash-domain.org http://dash2-domain2.org:8080 <a href="dash3-domain3.org/with/path">
    """
    logging.info(extractor.extracturis(txt))
