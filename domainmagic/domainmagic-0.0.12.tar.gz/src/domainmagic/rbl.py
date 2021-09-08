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

from domainmagic.tasker import TaskGroup, get_default_threadpool
from domainmagic.tld import get_default_tldmagic
from domainmagic.dnslookup import DNSLookup
from domainmagic.ip import ip_reversed
from domainmagic.validators import is_ip, is_hostname, is_email
from domainmagic.mailaddr import strip_batv, decode_srs, email_normalise_ebl, email_normalise_sh, email_normalise_low, domain_from_mail
import logging
import re
from string import Template
import os
import hashlib
import time
import io
import base64


filecache = {}


def remove_trailing_dot(input):
    """if input ends with a dot, remove it"""
    if input.endswith('.'):
        return input[:-1]
    else:
        return input


def add_trailing_dot(input):
    if not input.endswith('.'):
        return input + '.'
    else:
        return input


class RBLProviderBase(object):

    """Baseclass for all rbl providers"""

    def __init__(self, rbldomain, timeout=3, lifetime=10):
        self.replycodes = {}
        self.rbldomain = rbldomain
        self.logger = logging.getLogger('%s.rbllookup.%s' % (__package__, self.rbldomain))
        self.resolver = DNSLookup(timeout=timeout, lifetime=lifetime)
        self.descriptiontemplate = "${input} is listed on ${rbldomain} (${identifier})"
        self.lifetime = lifetime
        self.filters = None

    def add_replycode(self, mask, identifier=None):
        """add a replycode/bitmask. identifier is any object which will be returned if a dns result matches this replycode
        if identifier is not passed, the lookup domain will be used"""

        if identifier is None:
            identifier = self.rbldomain

        self.replycodes[mask] = identifier
        
    def add_filters(self, filters=None):
        self.filters = filters

    def _listed_identifiers(self, input, transform, dnsresult):
        listings = []
        for code, identifier in self.replycodes.items():
            if dnsresult == "%s" % code or dnsresult == "127.0.0.%s" % code:
                listings.append(
                    (identifier,
                     self.make_description(input=input,
                                           dnsresult=dnsresult,
                                           transform=transform,
                                           identifier=identifier,
                                           replycode=code)))
        return listings

    def make_description(self, **values):
        """create a human readable listing explanation"""
        template = Template(self.descriptiontemplate)
        values['rbldomain'] = self.rbldomain
        return template.safe_substitute(values)

    def accept_input(self, value):
        return re.match("^[a-zA-Z0-9.-]{2,256}$", value) is not None

    def transform_input(self, value):
        """transform input, eg, look up records or make md5 hashes here or whatever is needed for your specific provider and return a list of transformed values"""
        return [value, ]

    def make_lookup(self, transform):
        """some bls require additional modifications, even after input transformation, eg. ips must be reversed...
        by default we just fix trailing dots
        """
        return add_trailing_dot(transform) + self.rbldomain

    def listed(self, input, parallel=False):
        listings = []
        if not self.accept_input(input):
            self.logger.debug('value not acceptable: %s' % input)
            return []
        transforms = self.transform_input(input)

        if parallel:
            lookup_to_trans = {}
            for transform in transforms:
                lookup_to_trans[self.make_lookup(transform)] = transform

            logging.debug("lookup_to_trans=%s" % lookup_to_trans)

            multidnsresult = self.resolver.lookup_multi(lookup_to_trans.keys())

            for lookup, arecordlist in multidnsresult.items():
                if lookup not in lookup_to_trans:
                    self.logger.error("dns error: I asked for %s but got '%s' ?!" % (lookup_to_trans.keys(), lookup))
                    continue

                for ipresult in arecordlist:
                    listings.extend(self._listed_identifiers(input, lookup_to_trans[lookup], ipresult.content))
        else:
            loopstarttime = time.time()
            for transform in transforms:
                lookup = self.make_lookup(transform)
                arecordlist = self.resolver.lookup(lookup.encode('utf-8', 'ignore'))
                for ipresult in arecordlist:
                    listings.extend(
                        self._listed_identifiers(input, transform, ipresult.content))
                
                runtime = time.time() - loopstarttime
                if runtime > self.lifetime:
                    self.logger.debug('rbl lookup aborted due to timeout after %ss' % runtime)
                    break

        return listings

    def __str__(self):
        return "<%s d=%s codes=%s>" % (self.__class__.__name__, self.rbldomain, self.replycodes)

    def __repr__(self):
        return str(self)


class BitmaskedRBLProvider(RBLProviderBase):

    def _listed_identifiers(self, input, transform, dnsresult):
        """returns a list of identifiers matching the dns result"""
        listings = []
        lastoctet = dnsresult.split('.')[-1]
        for mask, identifier in self.replycodes.items():
            if int(lastoctet) & mask == mask:
                desc = self.make_description(
                    input=input,
                    transform=transform,
                    dnsresult=dnsresult,
                    identifier=identifier,
                    replycode=mask)
                listings.append((identifier, desc),)
        return listings


class ReverseIPLookup(RBLProviderBase):

    """IP lookups require reversed question"""

    def make_lookup(self, transform):
        if is_ip(transform):
            return ip_reversed(transform) + '.' + self.rbldomain
        else:
            return add_trailing_dot(transform) + self.rbldomain


class StandardURIBLProvider(ReverseIPLookup, BitmaskedRBLProvider):

    """This is the most commonly used rbl provider (uribl, surbl)
     - domains are A record lookups example.com.rbldomain.com
     - results are bitmasked
     - ip lookups are reversed
    """
    pass


class BitmaskedIPOnlyProvider(StandardURIBLProvider):

    """ ip only lookups
    lookups are reversed (inherited from StandardURIBLProvider)
    """

    def accept_input(self, value):
        return is_ip(value)


class FixedResultIPOnlyProvider(ReverseIPLookup, RBLProviderBase):

    """ ip only lookups, like zen
    lookups are reversed (inherited from StandardURIBLProvider)
    """

    def accept_input(self, value):
        return is_ip(value)


def valid_host_names(lookupresult):
    """return a list of valid host names from a  lookup result
    """
    validnames = set()
    for rec in lookupresult:
        content = rec.content
        content = remove_trailing_dot(content)
        if is_hostname(content, check_valid_tld=True):
            validnames.add(content)
    validnames = list(validnames)
    return validnames


class BlackNSNameProvider(StandardURIBLProvider):

    """Nameserver Name Blacklists"""

    def __init__(self, rbldomain, timeout=3, lifetime=10):
        StandardURIBLProvider.__init__(self, rbldomain, timeout=timeout, lifetime=lifetime)
        self.descriptiontemplate = "${input}'s NS name ${transform} is listed on ${rbldomain} (${identifier})"

    def transform_input(self, value):
        ret = []
        try:
            nsrecords = self.resolver.lookup(value, 'NS')
            return valid_host_names(nsrecords)

        except Exception as e:
            self.logger.warning("Exception in getting ns names: %s" % str(e))

        return ret


class BlackNSIPProvider(StandardURIBLProvider):

    """Nameserver IP Blacklists"""

    def __init__(self, rbldomain, timeout=3, lifetime=10):
        StandardURIBLProvider.__init__(self, rbldomain, timeout=timeout, lifetime=lifetime)
        self.descriptiontemplate = "${input}'s NSIP ${transform} is listed on ${rbldomain} (${identifier})"

    def transform_input(self, value):
        """transform input, eg, make md5 hashes here or whatever is needed for your specific provider"""
        ret = []
        try:
            nsnamerecords = self.resolver.lookup(value, 'NS')
            nsnames = valid_host_names(nsnamerecords)
            for nsname in nsnames:
                arecords = self.resolver.lookup(nsname, 'A')
                ips = [record.content for record in arecords]
                for ip in ips:
                    if not ip in ret:
                        ret.append(ip)
            
        except Exception as e:
            self.logger.warning("Exception in black ns ip lookup: %s" % str(e))

        return ret

    def make_lookup(self, transform):
        return ip_reversed(transform) + '.' + self.rbldomain


class BlackAProvider(StandardURIBLProvider):

    """A record blacklists"""

    def __init__(self, rbldomain, timeout=3, lifetime=10):
        StandardURIBLProvider.__init__(self, rbldomain, timeout=timeout, lifetime=lifetime)
        self.descriptiontemplate = "${input}'s A record ${transform} is listed on ${rbldomain} (${identifier})"

    def transform_input(self, value):
        try:
            arecords = self.resolver.lookup(value, 'A')
            ips = [record.content for record in arecords]
            return ips
        except Exception as e:
            self.logger.warning("Exception on a record lookup: %s" % str(e))

        return []


class SOAEmailProvider(StandardURIBLProvider):

    """Black SOA Email"""

    def __init__(self, rbldomain, timeout=3, lifetime=10):
        StandardURIBLProvider.__init__(self, rbldomain, timeout=timeout, lifetime=lifetime)
        self.descriptiontemplate = "${input}'s SOA email ${transform} is listed on ${rbldomain} (${identifier})"

    def transform_input(self, value):
        try:
            soaemails = []
            soarecords = self.resolver.lookup(value, 'SOA')
            if len(soarecords) == 0:
                domain = get_default_tldmagic().get_domain(value)
                soarecords = self.resolver.lookup(domain, 'SOA')
            
            for rec in soarecords:
                parts = rec.content.split()
                if len(parts) != 7:
                    continue
                email = remove_trailing_dot(parts[1])
                soaemails.append(email)

            return soaemails #TODO: is this correct or should we return hashes of the email addresses?
        except Exception as e:
            self.logger.warning("%s on SOA record lookup: %s" % (e.__class__.__name__, str(e)))
        return []


class EmailBLSimpleProvider(StandardURIBLProvider):
    """
    Simple EmailBL query provider.
    Returns one hash of normalised email address
    Hash and normalisation is determined by passed filters, defaults to md5 and lowercase only
    """
    
    def _get_domainlist(self):
        domainlist = None
        if not self.filters:
            return domainlist
        for item in self.filters:
            if item.startswith('file='):
                path = item.split('=')[-1]
                if os.path.exists(path):
                    now = time.time()
                    try:
                        values, ts = filecache[path]
                        if ts < now-600: # only read file every n seconds
                            values = None
                    except KeyError:
                        values = None
                    if values is not None:
                        domainlist = values
                    else:
                        with open(path) as f:
                            domainlist = f.readlines()
                            # remove trailing spaces & newlines
                            domainlist = [d.strip() for d in domainlist if d.strip()]
                            filecache[path] = (domainlist, now)
        return domainlist

    def accept_input(self, value):
        if not is_email(value):
            return False
        domainlist = self._get_domainlist()
        if domainlist is None: # no domainlist: accept every mail address
            return True
        domain = domain_from_mail(value)
        return domain in domainlist
    
    def _get_format(self):
        normalisers = {
            'low': email_normalise_low,
            'sh': email_normalise_sh,
            'ebl': email_normalise_ebl,
        }
        
        encoders = {
            'hex': lambda x: x.hexdigest(),
            'b64': lambda x: base64.b64encode(x.digest()).decode().rstrip('='),
            'b32': lambda x: base64.b32encode(x.digest()).decode().rstrip('='),
        }
    
        hashtype = 'md5'
        normaliser = email_normalise_low
        encoder = encoders['hex']
        if self.filters is None:
            pass
        else:
            for fltr in self.filters:
                if fltr in hashlib.algorithms_available:
                    hashtype = fltr
                elif fltr in normalisers:
                    normaliser = normalisers[fltr]
                elif fltr in list(encoders.keys()):
                    encoder = encoders[fltr]
                    
        return hashtype, normaliser, encoder

    def transform_input(self, value):
        hashtype, normaliser, encoder = self._get_format()
        value = normaliser(value)
        hasher = hashlib.new(hashtype, value.encode())
        return [encoder(hasher)]
    
    
    
class EmailBLMultiProvider(EmailBLSimpleProvider):
    """
    Complex EmailBL query provider
    Returns one or multiple hashes of various normalisations of email address
    Hash: anyone supported by hashlib, defaults to md5
    Normalisations:
        - lowercase only
        - strip batv tags + lowercase
        - decode srs + lowercase
        - according to normaliser definition (low/sh/ebl, including stripped batv and decoded srs)
    """
    
    def transform_inut(self, value):
        value = value.lower()
        values = [value]
        batvvalue = strip_batv(value)
        values.append(batvvalue.lower())
        srsvalue = decode_srs(value.lower())
        values.append(srsvalue)
        
        hashtype, normaliser, encoder = self._get_format()
        for value in list(set(values)):
            value = normaliser(value)
            values.append(value)
        
        hashes = []
        for v in list(set(values)):
            hasher = hashlib.new(hashtype, v.encode())
            hashes.append(encoder(hasher))
        
        return hashes
    


class FixedResultDomainProvider(RBLProviderBase):

    """uribl lookups with fixed return codes and ip lookups disabled, like the spamhaus DBL"""

    def accept_input(self, value):
        if not super(FixedResultDomainProvider, self).accept_input(value):
            return False

        if is_ip(value):  # dbl is the only known fixed result domain provider and does not allow ip lookups, so we filter this here
            return False

        return True


class RBLLookup(object):

    def __init__(self, timeout=3, lifetime=10):
        self.logger = logging.getLogger('%s.rbllookup' % __package__)
        self.providers = []
        self.resolver = DNSLookup(timeout=timeout, lifetime=lifetime)
        self.timeout = timeout
        self.lifetime = lifetime

        self.providermap = {
            'uri-bitmask': StandardURIBLProvider,
            'ip-bitmask': BitmaskedIPOnlyProvider,
            'ip-fixed': FixedResultIPOnlyProvider,
            'domain-fixed': FixedResultDomainProvider,
            'nsip-bitmask': BlackNSIPProvider,
            'nsname-bitmask': BlackNSNameProvider,
            'a-bitmask': BlackAProvider,
            'email-bitmask': EmailBLSimpleProvider,
            'multi-email-bitmask': EmailBLMultiProvider,
            'soaemail-bitmask': SOAEmailProvider,
        }
    
    
    def from_config(self, filepath=None):
        self.logger.debug('loading rbl lookups from file %s' % filepath)
        if not os.path.exists(filepath):
            self.logger.error("File not found: %s" % filepath)
            return

        providers = []

        with io.open(filepath) as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue

            parts = line.split(None, 2)
            if len(parts) != 3:
                self.logger.error("invalid config line: %s" % line)
                continue

            providertype, searchdomain, resultconfig = parts
            if providertype not in self.providermap:
                self.logger.error("unknown provider type %s for %s" % (providertype, searchdomain))
                continue

            providerclass = self.providermap[providertype]

            providerinstance = providerclass(searchdomain, timeout=self.timeout, lifetime=self.lifetime)
            providerinstance.resolver = self.resolver

            # set bitmasks and filters
            for res in resultconfig.split():
                filters = None
                if ':' in res:
                    fields = res.split(':')
                    try:
                        code = int(fields[0])
                    except (ValueError, TypeError):
                        # fixed value
                        code = fields[0]
                    identifier = fields[1]
                    if len(fields)>2:
                        filters = fields[2:]
                else:
                    identifier = res
                    code = 2

                providerinstance.add_replycode(code, identifier)
                providerinstance.add_filters(filters)
            providers.append(providerinstance)
        self.providers = providers
        self.logger.debug("Providerlist from configfile: %s" % providers)
    
    
    def listings(self, domain, timeout=10, parallel=False, abort_on_hit=False):
        """return a dict identifier:humanreadable for each listing
        warning: parallel is very experimental and has bugs - do not use atm
        """
        listed = {}

        if parallel:
            tg = TaskGroup()
            for provider in self.providers:
                tg.add_task(provider.listed, (domain,), )
            threadpool = get_default_threadpool()
            threadpool.add_task(tg)
            tg.join(timeout)

            for task in tg.tasks:
                if task.done:
                    for identifier, humanreadable in task.result:
                        listed[identifier] = humanreadable
            threadpool.stayalive = False
        else:
            starttime = time.time()
            for provider in self.providers:
                loopstarttime = time.time()
                runtime = loopstarttime - starttime
                if timeout > 0 and runtime > timeout:
                    self.logger.info('lookups aborted after %.2fs due to timeout' % runtime)
                    break
                
                for identifier, humanreadable in provider.listed(domain):
                    listed[identifier] = humanreadable
                    if abort_on_hit:
                        return listed.copy()
                
                self.logger.debug('%s completed in %.2fs' % (provider.rbldomain, time.time()-loopstarttime))

        return listed.copy()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("usage: rbl </path/to/rbl.conf> <domain> [-debug]")
        sys.exit(1)

    rbl = RBLLookup()
    rbl.from_config(sys.argv[1])

    if '-debug' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)

    query = sys.argv[2]

    start = time.time()
    ans = rbl.listings(query)
    end = time.time()
    diff = end - start
    for ident, expl in ans.items():
        print("identifier '%s' because: %s" % (ident, expl))

    print("")
    print("execution time: %.4f" % diff)
    sys.exit(0)
