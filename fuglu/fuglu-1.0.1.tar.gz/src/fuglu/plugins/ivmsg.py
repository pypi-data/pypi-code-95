# -*- coding: UTF-8 -*-
import re
import traceback
import typing as tp
import ipaddress

from fuglu.extensions.redisext import RedisPooledConn, ENABLED as REDIS_ENABLED
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin
from fuglu.shared import _SuspectTemplate, FuConfigParser, ScannerPlugin, get_outgoing_helo, DUNNO, FileList
from fuglu.stringencode import force_uString
import os
import sys


class IVMSendgrid(BMPRCPTMixin, BasicMilterPlugin):
    
    """
    reject mail from abused sendgrid customer IDs
    uses invaluement service provider dnsbl from
    https://www.invaluement.com/serviceproviderdnsbl/
    which is stored in redis.
    
    periodically load data into redis using the IVMImport command line client:
    python3 ivmsg.py [path/to/config]
    """
    
    def __init__(self,config):
        super().__init__(config)
        self.logger = self._logger()
        self.redis_pool = None
        
        self.requiredvars={
            'redis_conn': {
                'default': '',
                'description': 'redis backend database connection: redis://host:port/dbid',
            },
            
            'redis_timeout': {
                'default': '2',
                'description': 'redis backend timeout in seconds',
            },
            
            'rejectmessage': {
                'default': 'sender blacklisted (IVM-SG)',
                'description': 'reject message template for policy violators'
            },

            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            
            'redis_ttl': {
                'default': '86400',
                'section': 'IVMImport',
                'description': 'how long should imported values remain in redis'
            },
            
            'ivm_file': {
                'default': '',
                'section': 'IVMImport',
                'description': 'path to downloaded invaluement service provider dnsbl file'
            },
            
            'senderhost_domains': {
                'default': 'sendgrid.com',
                'description': 'comma separated list of sender host domains to evaluate'
            },
            
            'senderhost_cidr_file': {
                'default': '${confdir}/ivmsg_senderhost_cidr.txt',
                'description': 'path to cidr file, contains one sender host cidr per line'
                # hint: you may want to list AS11377 in that file
            },
        }
        
        self.cidrlist = None
    
    
    def _init_redisconn(self):
        if self.redis_pool is None:
            redisconn = self.config.get(self.section, 'redis_conn')
            timeout = self.config.getint(self.section, 'redis_timeout')
            self.redis_pool = RedisPooledConn(redisconn, socket_keepalive=True, socket_timeout=timeout)
    
    
    
    def _init_cidrlist(self):
        if self.cidrlist is None:
            filepath = self.config.get(self.section, 'senderhost_cidr_file')
            if filepath and os.path.exists(filepath):
                self.cidrlist = FileList(filename=filepath, additional_filters=self._cidrconvert)
    
    
    def _cidrconvert(self, value):
        try:
            cidr = ipaddress.ip_network(value)
        except ValueError:
            cidr = None
            self.logger.error('not a CIDR: %s' % value)
        return cidr
    
    
    def _in_sg_cidr(self, clientip):
        self._init_cidrlist()
        if self.cidrlist is None:
            self.logger.error('no CIDR list loaded')
            return False
        cidrlist = self.cidrlist.get_list()
        ip = ipaddress.ip_address(clientip)
        for cidr in cidrlist:
            if ip in cidr:
                return True
        return False
    
    
    def _in_senderhostlist(self, remotehostname):
        senderhostlist = self.config.getlist(self.section, 'senderhost_domains')
        for host in senderhostlist:
            if remotehostname == host or remotehostname.endswith(f'.{host}'):
                return True
        return False
        
    
    
    def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        if not REDIS_ENABLED:
            self.logger.debug("No redis -> skip plugin...")
            return sm.CONTINUE

        self._init_redisconn()
        sender = force_uString(sess.sender)
        clientip = force_uString(sess.addr)

        # we used client_address here for postomaat...
        remotehostname = force_uString(sess.fcrdns)

        self.logger.debug(f"{sess.id} sender:{sender}, clientip:{clientip}, remotehostname:{remotehostname}")

        # it's possible to get an error talking to redis, several attempts can help
        attempts = 2
        while attempts:
            attempts -= 1
            try:
                if sender.startswith('bounces+') and (self._in_senderhostlist(remotehostname) or self._in_sg_cidr(clientip)):
                    self.logger.debug(f'{sess.id} is a sendgrid sender {sender}')
                    r = re.search('^bounces\+(?P<sgid>[0-9]{4,10})-[0-9a-z]{4}-', sender)
                    if r:
                        sgid = r.groups('sgid')[0]

                        redisconn = self.redis_pool.get_conn()
                        key = 'ivmsg-%s' % sgid
                        listed = redisconn.exists(key)
                        if listed:
                            template = _SuspectTemplate(self.config.get(self.section, 'rejectmessage'))
                            message = template.safe_substitute(sess.get_templ_dict())
                            return sm.REJECT, message
                        else:
                            self.logger.info(f'{sess.id} sgid {sgid} from {sender} is not listed')
                    else:
                        self.logger.warning(f'{sess.id} no regex match for sendgrid sender {sender}')

                else:
                    self.logger.debug(f'{sess.id} not a sendgrid sender {sender}')
                # exit while loop
                attempts = 0
            except Exception as e:
                msg = f'{sess.id} ivm-sendgrid plugin failed with error {type(e)} for sender {sender}: {str(e)}'
                if attempts:
                    # if there are attempts left, log a warning only
                    self.logger.warning(msg)
                else:
                    # if there are no attempts left, log as error
                    self.logger.error(msg)
            
        return sm.CONTINUE
    
    
    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True

        lint_ok = True
        if not self.checkConfig():
            print('Error checking config')
            lint_ok = False
        
        if lint_ok:
            self._init_cidrlist()
            if self.cidrlist is None:
                print('ERROR: no CIDR list loaded')
                lint_ok = False
    
        if not REDIS_ENABLED:
            print('ERROR: redis not available - this plugin will do nothing')
            lint_ok = False
        
        if lint_ok:
            self._init_redisconn()
            lint_ok = self.redis_pool.check_connection()
            if not lint_ok:
                print('ERROR: failed to ping redis server')
    
        return lint_ok



class IVMFeed(ScannerPlugin):
    """
    augment your redis database of abused sendgrid ids with data from your own traps
    """
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.redis_pool = None
        self._from_hdr = None
        
        self.requiredvars = {
            'redis_conn' : {
                'default':'',
                'description':'redis backend database connection',
            },
            
            'redis_timeout':{
                'default':'2',
                'description':'redis backend timeout in seconds',
            },
            
            'ttl': {
                'default': '14400',
                'description': 'redis ttl',
            },
            
            'sender_domains': {
                'default': 'sendgrid.net',
                'description': 'comma separated list of sender domains to consider for check'
            },
            
            'sender_headers': {
                'default': 'Return-Path, X-Original-Sender',
                'description': 'comma separated list of headers that may contain a sender address'
            },
        }
    
    
    def _init_redisconn(self):
        if self.redis_pool is None:
            redisconn = self.config.get(self.section, 'redis_conn')
            timeout = self.config.getint(self.section, 'redis_timeout')
            self.redis_pool = RedisPooledConn(redisconn, socket_keepalive=True, socket_timeout=timeout)
    
    
    def _get_hdr_from(self, suspect):
        if self._from_hdr is None:
            hdr_from_addresses = suspect.parse_from_type_header(header='From', validate_mail=True)
            if hdr_from_addresses and len(hdr_from_addresses[0])==2 and '@' in hdr_from_addresses[0][1]:
                hdr_from_display, hdr_from_address = hdr_from_addresses[0]
            else:
                hdr_from_address='unknown'
            self._from_hdr = hdr_from_address
        return self._from_hdr
    
    
    def _in_sender_domain(self, senderdomain):
        sender_domains = self.config.getlist(self.section, 'sender_domains')
        for sdrdom in sender_domains:
            if senderdomain == sdrdom or senderdomain.endswith(f'.{sdrdom}'):
                return True
        return False
        
    
    
    def examine(self, suspect):
        if not REDIS_ENABLED:
            return DUNNO
        
        msgrep = suspect.get_message_rep()
        senders = [suspect.from_address]
        for header in self.config.getlist(self.section, 'sender_headers'):
            senders.append(msgrep.get(header))
        senders = [s for s in senders if s and '@' in s]
        
        for sender in senders:
            try:
                lhs, domain = sender.rsplit('@', 1)
                if lhs and lhs.startswith('bounces+') and self._in_sender_domain(domain):
                    r = re.search('^bounces\+(?P<sgid>[0-9]{5,10})-[0-9a-z]{4}-', sender)
                    sgid = r.groups('sgid')[0]
                    
                    if not sgid:
                        self.logger.error('%s no sgid found in sender=%s' % (suspect.id, sender))
                    else:
                        hdr_from_address = self._get_hdr_from(suspect)
                        self._init_redisconn()
                        key = 'ivmsg-%s' % sgid
                        line = f'source={get_outgoing_helo(self.config)} from={hdr_from_address}'
                        ttl = self.config.getint(self.section, 'ttl')
                        redisconn = self.redis_pool.get_conn()
                        redisconn.set(key, line, ttl)
                        self.logger.info('%s blocked sgid=%s hdr_from=%s' % (suspect.id, sgid, hdr_from_address))
            except ConnectionResetError as e:
                self.logger.warning('%s failed to run ivmfeed, error=%s' % (suspect.id, str(e)))
            except Exception as e:
                self.logger.debug('%s %s' % (suspect.id, traceback.format_exc()))
                self.logger.error('%s failed to run ivmfeed, error=%s' % (suspect.id, str(e)))
            
        self._from_hdr = None
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if ok:
            self._init_redisconn()
            if not self.redis_pool.check_connection():
                print('ERROR: failed to ping redis server')
                ok = False
        return ok


class IVMImport(object):
    def __init__(self, configfile):
        self.config = FuConfigParser()
        if os.path.exists(configfile):
            self.config.read_file(configfile)
        else:
            print(f'ERROR: no such config {configfile}')
        self.section = self.__class__.__name__
        self.ivmsgplugin = IVMSendgrid(self.config)
    
    
    def load_file(self, ivm_file):
        content = None
        if ivm_file and os.path.exists(ivm_file):
            with open(ivm_file, 'rb') as f:
                content = f.read()
        return content
    
    
    def parse_data(self, content):
        # the default file contains one sendgrid customer id per line
        lines = []
        if content:
            lines = [l for l in content.decode().splitlines() if not l.startswith('#')]
        return lines
    
    
    def store_data(self, data, source):
        redis_ttl = self.ivmsgplugin.config.getint(self.section, 'redis_ttl')
        self.ivmsgplugin._init_redisconn()
        redisconn = self.ivmsgplugin.redis_pool.get_conn()
        for sgid in data:
            key = 'ivmsg-%s' % sgid
            line = 'source=%s' % source
            redisconn.set(key, line, redis_ttl)
    
    
    def process(self):
        ivm_file = self.ivmsgplugin.config.get(self.section, 'ivm_file')
        content = self.load_file(ivm_file)
        data = self.parse_data(content)
        self.store_data(data, ivm_file)


if __name__ == '__main__':
    if len(sys.argv)>1:
        cf = sys.argv[1]
    else:
        cf = '/etc/fuglu/conf.d/ivmsg.conf'
    ivmimport = IVMImport(cf)
    ivmimport.process()
