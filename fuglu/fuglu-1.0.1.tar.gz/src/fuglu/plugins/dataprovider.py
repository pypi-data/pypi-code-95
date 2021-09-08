#!/usr/bin/python3
# -*- coding: utf-8 -*-
#   Copyright 2009-2021 Oli Schacher, Fumail Project
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
from fuglu.shared import ScannerPlugin, DUNNO, FileList
from fuglu.stringencode import force_uString, force_bString
import socket
import logging
import time
import string
import re
import os
import fcntl
from urllib.parse import urlparse



def parse_targets(targetlist):
    targets = []
    errors = {}
    
    for target in targetlist:
        try:
            host, port = target.rsplit(':', -1)
        except ValueError:
            errors[target] = 'not a valid host:port definition %s' % target
            continue
        try:
            port = int(port)
        except (TypeError, ValueError):
            errors[target] = 'not a valid port number %s' % port
            continue
        host = host.strip('[]') # ipv6
        targets.append((host, port))
    
    return targets, errors



class CBLFeeder(object):
    
    def __init__(self,targets):
        self.targets = targets
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.logger = logging.getLogger('fuglu.cblfeed.CBLFeeder')
        
    
    def feed(self,ip,helo,rdns=None,timestamp=None):
        if timestamp is None:
            timestamp=int(time.time())
        
        helo=self.normalize_helo(helo)
        
        packet="%s\t%s\t%s"%(ip,helo,timestamp)
        if rdns is not None and rdns.strip() not in ['','unknown']:
            packet+="\t%s"%rdns

        self.logger.info("CBL Feed: ip=%s helo=%s rdns=%s"%(ip,helo,rdns))
        if self.targets:
            for host, port in self.targets:
                self.sock.sendto(force_bString(packet), (host, port))
        else:
            return packet
        
    
    def normalize_helo(self,helo):
        return "".join([self._replace_char(x) for x in helo])
    
    
    def _replace_char(self,char):
        od=ord(char)
        if od>32 and od <127 and char not in string.whitespace :
            return char
        ret= "\\x{0:02x}".format(od)
        return ret



class CBLFeederPlugin(ScannerPlugin):
    """
    The plugin feeds CBL with bot connection information from spamtraps.
    Spamhaus CBL/XBL data feedback
    (Based on Version 2.2, November 2012)
    """
    
    def __init__(self,config,section=None):
        ScannerPlugin.__init__(self,config,section)
        self.logger = self._logger()
        self.feed=None
        self.requiredvars={
            'targets': {
                'default': '',
                'description': 'list of udpfeeder targets host:port',
            },
            
            'ignoreipregex': {
                'default': "",
                'description': """if the client ip matches this regex, do not feed"""
            },
        }
    
    
    def _init_feed(self):
        if self.feed is None:
            targetlist = self.config.getlist(self.section, 'targets')
            targets, errors = parse_targets(targetlist)
            for error in errors:
                self.logger.error('%s in target %s' % (errors[error], error))
            
            self.feed=CBLFeeder(targets)
    
    
    def examine(self, suspect):
        return self._run(suspect)
    
    
    def process(self, suspect, decision):
        self._run(suspect)
    
    
    def _run(self, suspect):
        self._init_feed()
        
        clientinfo=suspect.get_client_info(config=self.config)
        if clientinfo is None:
            self.logger.debug('%s no client info found' % suspect.id)
            return DUNNO
        helo,ip,rdns=clientinfo
        
        if helo is None or helo=='':
            self.logger.debug('%s no client helo found' % suspect.id)
            return DUNNO
        
        ignoreipregex=self.config.get(self.section,"ignoreipregex").strip()
        if ignoreipregex!="":
            if re.match(ignoreipregex, ip) is not None:
                self.logger.debug('%s ignoring IP %s' % (suspect.id, ip))
                return DUNNO
        if rdns=='unknown':
            rdns=None
        
        self.feed.feed(ip, helo, rdns)
        return DUNNO
    
    
    def lint(self):
        if not self.check_config():
            return False
        
        targetlist = self.config.getlist(self.section, 'targets')
        targets, errors = parse_targets(targetlist)
        if not targets and not errors:
            print('INFO: no targets defined, this plugin will do nothing')
        elif errors:
            for error in errors:
                print('ERROR: %s in target %s' % (errors[error], error))
            return False
        else:
            print('INFO: feeding to targets: %s' % targets)

        self._init_feed()
        self.feed.targets = None
        packet = self.feed.feed('1.2.3.4', 'helo.example.com', 'ptr.example.com')
        print('INFO: sample packet: %s' % packet)
        
        return True
    
        
    def __str__(self):
        return "CBL Feed"



class URIUDPSend(ScannerPlugin):
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        
        self.requiredvars = {
            'targets': {
                'default': '',
                'description': 'list of udpfeeder targets host:port',
            },
            
            'mapsection': {
                'default': 'URIMapping',
                'description': 'name of config section containing mappings',
            },
            
            'default': {
                'section': 'URIMapping',
                'default': 'feed',
                'description': 'default mapping source',
            },
            
            'body_tags': {
                'default': 'body.uris uris.safelinks',
                'description': 'send body URIs listed in given tags (list tags white space separated)'
            },
            
            'att_tags': {
                'default': 'headers.uris',
                'description': 'send attachment URIs listed in given tags (list tags white space separated)'
            },
            
            'att_source': {
                'default': 'docpdf',
                'description': 'static mapping source for uris found in attachments'
            },
            
            'skip_source': {
                'default': 'ham',
                'description': 'skip sending if rcpt maps to this source'
            },
            
            'log_only': {
                'default': 'false',
                'description': 'log only without sending'
            },
        }
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    
    
    def _get_source(self, recipient):
        section = self.config.get(self.section, 'mapsection')
        if self.config.has_option(section, recipient):
            source = self.config.get(section, recipient).strip()
        else:
            source = self.config.get(section, 'default').strip()
        return force_bString(source)
    
    
    
    def _send_udp(self, suspect, uris):
        logonly = self.config.getboolean(self.section, 'log_only')
        sid = force_bString(suspect.id)
        targetlist = self.config.getlist(self.section, 'targets')
        targets, errors = parse_targets(targetlist)
        for error in errors:
            self.logger.error('%s %s in target %s' % (suspect.id, errors[error], error))
        for host, port in targets:
            for uri, source in uris:
                if logonly:
                    self.logger.info(f"{suspect.id} LOGONLY: uri={force_uString(uri)} src={force_uString(source)} sid={force_uString(sid)}")
                else:
                    content = b'%s\n%s\n%s' % (force_bString(uri.strip()), source, sid)
                    self.sock.sendto(content, (host, port))
                    self.logger.debug(f"{suspect.id} SENT: uri={force_uString(uri)} src={force_uString(source)} sid={force_uString(sid)} to {host}:{port}")
    
    
    def _get_uris(self, suspect, tags):
        uris = []
        for tag in tags:
            uris.extend(suspect.get_tag(tag, []))
        return uris



    def examine(self, suspect):
        return self._run(suspect)


    def process(self, suspect, decision):
        self._run(suspect)


    def _run(self, suspect):
        source = self._get_source(suspect.to_address)
        if source == force_bString(self.config.get(self.section, 'skip_source')):
            return DUNNO
        
        body_tags = self.config.getlist(self.section, 'body_tags', separators=' ')
        uris = self._get_uris(suspect, body_tags)
        
        urilist = []
        for uri in uris:
            urilist.append((uri, source))
        
        att_tags = self.config.getlist(self.section, 'att_tags', separators=' ')
        uris = self._get_uris(suspect, att_tags)
        attsrc = force_bString(self.config.get(self.section, 'att_source'))
        for uri in uris:
            urilist.append((uri, attsrc))
        
        self._send_udp(suspect, urilist)
        self.logger.info('%s sent %s URIs' % (suspect.id, len(urilist)))
    
    
    
    def lint(self):
        """lint check"""
        if not self.check_config():
            return False

        section = self.config.get(self.section, 'mapsection')
        if not self.config.has_section(section):
            print('WARNING: config section for mappings {mapsection} not found')
            return False
        
        source = self.config.get(section, 'default').strip()
        if not source:
            print('WARNING: no default mapping source defined')
            return False
        
        targetlist = self.config.getlist(self.section, 'targets')
        targets, errors = parse_targets(targetlist)
        if not targets and not errors:
            print('INFO: no targets defined, this plugin will do nothing')
        if errors:
            for error in errors:
                print('ERROR: %s in target %s' % (errors[error], error))
            return False
        
        return True





class URLTypeMap(FileList):
    def __init__(self, *args, **kwargs):
        FileList.__init__(self, *args, **kwargs)
        if isinstance(self.content, list):
            self.content = {}
    
    
    def _parse_lines(self, lines):
        newcontent = {}
        
        for line in lines:
            line = self._apply_linefilters(line)
            if not line:
                continue
            if not ':' in line:
                self.logger.debug('ignoring invalid line: %s' % line)
                # print('ignoring invalid line: %s' % line)
                continue
            
            urltype, lhsstring = line.split(':', 1)
            lhslist = [l.strip() for l in lhsstring.split(',')]
            for item in lhslist:
                try:
                    newcontent[item].append(urltype)
                    # print(f'extended {item} with {urltype}')
                except KeyError:
                    newcontent[item] = [urltype]
                    # print(f'created {item} with value {urltype}')

        # print(newcontent)
        return newcontent
    
    
    
    def get(self, item):
        """Returns the current list. If the file has been changed since the last call, it will rebuild the list automatically."""
        if self.filename is not None:
            self._reload_if_necessary()
        return self.content.get(item, [])



class URIWriter(ScannerPlugin):
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.urltype_map = None
        
        self.requiredvars = {
            'path_template': {
                'default': '/var/tmp/${urltype}-uris.txt',
                'descritption': 'template string where to place uris of a certain category'
            },
            
            'urltype_map_file': {
                'default': '${confdir}/uriwriter_urltypes.txt',
                'description': 'maps rcpt user name to url type categories'
            },
            
            'ignore_domains': {
                'default': 'microsoft.com avast.com w3c.org',
                'description': 'list of domains to be skipped'
            },
            
            'uri_tags': {
                'default': 'body.uris uris.safelinks headers.uris',
                'description': 'use URIs listed in given tags (list tags white space separated)'
            },
        }
    
    
    
    def _init_urltype_map(self):
        if self.urltype_map is None:
            self.urltype_map = URLTypeMap(filename=self.config.get(self.section, 'urltype_map_file'))
    
    
    
    def _get_uris(self, suspect):
        tags = self.config.getlist(self.section, 'uri_tags', separators=' ')
        uris = []
        for tag in tags:
            uris.extend(suspect.get_tag(tag, []))
        return uris
    
    
    
    def _exclude_uris(self, uris):
        excludes = self.config.getlist(self.section, 'ignore_domains', separators=' ')
        newuris = []
        for uri in uris:
            p = urlparse(uri)
            for e in excludes:
                if not p.netloc == e and not p.netloc.endswith(f'.{e}'):
                    newuris.append(uri)
        return newuris
    
    
    def _lock_acquire(self, filedesc, timeout=30):
        endtime = time.time()+timeout
        acquired = False
        while not acquired:
            try:
                fcntl.lockf(filedesc, fcntl.LOCK_EX|fcntl.LOCK_NB)
                acquired = True
            except BlockingIOError:
                if time.time() >= endtime:
                    break
                time.sleep(0.1)
        return acquired
    
    
    def _lock_release(self, filedesc):
        fcntl.lockf(filedesc, fcntl.LOCK_UN)
    
    
    
    def _write_data(self, suspect, urltype, uris):
        tmpl = string.Template(self.config.get(self.section, 'path_template'))
        filename = tmpl.safe_substitute(dict(urltype=urltype))
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname) and not os.path.isdir(dirname):
            self.logger.error(f'{suspect.id} cannot write file {filename} to inexisting dir {dirname}')
        else:
            with open(filename, 'a') as filedesc:
                if self._lock_acquire(filedesc, timeout=2):
                    try:
                        for uri in uris:
                            filedesc.write(f'{uri}\n')
                        filedesc.flush()
                        self.logger.debug(f'{suspect.id} wrote {len(uris)} uris to {filename}')
                    except Exception as e:
                        self.logger.error(f'{suspect.id} error writing uris to {filename} due to {str(e)}')
                    finally:
                        self._lock_release(filedesc)
                else:
                    self.logger.warning(f'{suspect.id} failed to get lock for file {filename}')



    def examine(self, suspect):
        return self._run(suspect)


    def process(self, suspect, decision):
        self._run(suspect)


    def _run(self, suspect):
        uris = self._get_uris(suspect)
        uris = self._exclude_uris(uris)
        uris = list(set(uris))
        if not uris:
            self.logger.debug(f'{suspect.id} no URIs to write')
            return DUNNO
        
        self._init_urltype_map()
        rcpt = suspect.to_localpart
        urltypes = self.urltype_map.get(rcpt)
        # self.logger.info(f'{suspect.id} writing {len(uris)} uris for {len(urltypes)} urltypes for rcpt {rcpt}')
        for urltype in urltypes:
            self._write_data(suspect, urltype, uris)
        
        return DUNNO
    
    
    
    def lint(self):
        if not self.check_config():
            print('ERROR: config error')
            return False
        
        filepath = self.config.get(self.section, 'urltype_map_file')
        if not os.path.exists(filepath):
            print(f'ERROR: cannot find urltypes file {filepath}')
            return False
        
        self._init_urltype_map()
        # print(self.urltype_map.content)
        if self.urltype_map is None:
            print('ERROR: urltype map not loaded')
            return False
        else:
            print('loaded %s mappings' % len(self.urltype_map.content))
        
        return True
    




### TEST CODE ###

if __name__=='__main__':
    feeder=CBLFeeder(None)
    assert feeder.normalize_helo("foo bar\tblatta\xff")=="foo\\x20bar\\x09blatta\\xff"
    feeder.feed("1.2.3.4", "döner mit scharf", "1.2.3.4")
    
    
    
#local test
# """
# import socket
# 
# sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# sock.bind(('127.0.0.1',1387))
# while True:
#     data, addr = sock.recvfrom(1024)
#     print data
# """