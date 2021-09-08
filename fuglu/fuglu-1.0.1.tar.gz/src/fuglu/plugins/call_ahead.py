#!/usr/bin/python
# -*- coding: UTF-8 -*-
#   Copyright 2012-2021 Fumail Project
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
import sys
#in case the tool is not installed system wide (development...)
if __name__ =='__main__':
    sys.path.append('../../')

import smtplib
from string import Template
import logging
from datetime import datetime, timedelta
import os
import re
import time
import threading
import typing as tp
import ssl

try:
    from domainmagic.mailaddr import strip_batv
    HAVE_DOMAINMAGIC = True
except ImportError:
    HAVE_DOMAINMAGIC = False

import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin
from fuglu.shared import _SuspectTemplate, Cache, FuConfigParser
from fuglu.stringencode import force_uString
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, DBConfig
from fuglu.extensions.dnsquery import lookup, DNSQUERY_EXTENSION_ENABLED, mxlookup
from fuglu.extensions.redisext import RedisPooledConn, ENABLED as REDIS_ENABLED, REDIS2
from fuglu.scansession import TrackTimings

DATEFORMAT = '%Y-%m-%d %H:%M:%S'

RE_IPV4 = re.compile(
    """(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)""")
RE_IPV6 = re.compile(
    """(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))""")


def get_config(fugluconfigfile=None, dconfdir=None):
    newconfig = FuConfigParser()
    logger = logging.getLogger('%s.shared' % __package__ if __package__ else "fuglu")

    if fugluconfigfile is None:
        fugluconfigfile = '/etc/fuglu/fuglu.conf'

    if dconfdir is None:
        dconfdir = '/etc/fuglu/conf.d'

    with open(fugluconfigfile) as fp:
        newconfig.read_file(fp)

    # load conf.d
    if os.path.isdir(dconfdir):
        filelist = os.listdir(dconfdir)
        configfiles = [dconfdir + '/' + c for c in filelist if c.endswith('.conf')]
        logger.debug('Conffiles in %s: %s' % (dconfdir, configfiles))
        readfiles = newconfig.read(configfiles)
        logger.debug('Read additional files: %s' % readfiles)
    return newconfig


class BackendMixin(object):
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.cache = None
        self.config_backend = None
    
    
    def _init_cache(self, config=None, section=None):
        if config is None:
            config = self.config
        if section is None:
            section = self.section
        if self.cache is None:
            storage = config.get(section, 'cache_storage')
            if storage == 'sql':
                self.cache = MySQLCache(config, section)
            elif storage == 'redis':
                self.cache = RedisCache(config, section)
            elif storage == 'memory':
                self.cache = MemoryCache(config, section)


    def _init_config_backend(self, recipient, config=None, section=None):
        if config is None:
            config = self.config
        if section is None:
            section = self.section
        if self.config_backend is None:
            backend = config.get(section, 'config_backend')
            if backend == 'sql':
                self.config_backend = MySQLConfigBackend(config, section)
            elif backend == 'dbconfig':
                self.config_backend = DBConfigBackend(config, section)
            elif backend == 'file':
                self.config_backend = ConfigFileBackend(config, section)
        self.config_backend.set_rcpt(recipient)



class AddressCheck(BMPRCPTMixin, BasicMilterPlugin, BackendMixin):
    """
    Flexibly query if a recipient exists on target server.
    Query result is cached in a global database (sql or redis).
    To reliably determine existing recipients, the target server must support recipient filtering and give a proper
    SMTP response after RCPT TO. 2xx for existing users, 5xx for non-existing users.
    To determine recipient filtering availability we test against a "random" user. If such user would be accepted
    the target server is added to a skiplist.
    
    Config Backend SQL:
CREATE TABLE `ca_configoverride` (
  `domain` varchar(255) NOT NULL,
  `confkey` varchar(255) NOT NULL,
  `confvalue` varchar(255) NOT NULL,
  PRIMARY KEY (`domain`,`confkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    SQL Cache storage:
CREATE TABLE `ca_skiplist` (
  `relay` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `check_ts` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `expiry_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `check_stage` varchar(20) DEFAULT NULL,
  `reason` varchar(400) DEFAULT NULL,
  PRIMARY KEY (`relay`,`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ca_addresscache` (
  `email` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `check_ts` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `expiry_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `positive` tinyint(1) NOT NULL,
  `message` text DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    """
    def __init__(self,config,section=None):
        super().__init__(config,section)
        self.logger = self._logger()
        self.relaycache = Cache()
        self.enabletimetracker = False
        
        self.requiredvars = {
            'cache_storage': {
                'default': 'sql',
                'description': 'the storage backend, one of sql, redis, memory. memory is local only.',
            },
            
            'config_backend': {
                'default': 'sql',
                'description': """the config backend, choose one of:
                sql (postomaat compatible sql query)
                dbconfig (use fuglu dbconfig)
                file (static config file)
                """,
            },
            
            'dbconnection':{
                'default':"mysql://root@localhost/callahead?charset=utf8",
                'description':'SQLAlchemy connection string for sql backend and sql config',
            },
            
            'redis_conn':{
                'default':'redis://127.0.0.1:6379/1',
                'description':'redis backend database connection: redis://host:port/dbid',
            },
            
            'redis_timeout':{
                'default':'2',
                'description':'redis backend timeout in seconds',
            },
            
            'redis_password': {
                'default': '',
                'description': 'password to connect to redis database. leave empty for no password',
            },
            
            'cleanupinterval':{
                'default':'300',
                'description':'memory backend cleanup interval',
            },
             
            'always_assume_rec_verification_support':{
                'default': "False",
                'description': """set this to true to disable the skiplisting of servers that don't support recipient verification"""
            }, 
                           
            'always_accept':{
                'default': "False",
                'description': """Set this to always return 'continue' but still perform the recipient check and fill the cache (learning mode without rejects)"""
            },
                           
            'keep_positive_history_time':{
                'default': '30',
                'description': """how long should expired positive cache data be kept in the table history [days] (sql only)"""
            },
                           
            'keep_negative_history_time':{
                'default': '1',
                'description': """how long should expired negative cache data be kept in the table history [days] (sql only)"""
            },
    
            'messagetemplate': {
                'default': 'previously cached response: ${message}',
                'description': 'reject message template for previously cached responses'
            },
            
            'messagetemplate_directory_only': {
                'default': 'User unknown',
                'description': 'reject message template in positive directory mode'
            },
            
            'always_accept_regex': {
                'default': '',
                'description': 'always accept recipients if they match this regex. leave empty to omit'
            },
            
            'enabled': {
                'section': 'ca_default',
                'default': 'True',
                'description': 'enable recipient verification',
            },
            
            'positive_directory_only': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'if set to True, do not perform call-ahead and consider missing entries in database to be negative/rejectable. This is useful if the entries for this domain are added via alternative means to the database (e.g. hardcoded or imported from a database/active directory/user listing)',
            },
            
            'timeout': {
                'section': 'ca_default',
                'default': '30',
                'description': 'socket timeout',
            },
            
            'testuser': {
                'section': 'ca_default',
                'default': 'rbxzg133-7tst',
                'description': 'test user that probably does not exist',
            },
            
            'test_server_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if it doesn't support recipient verification [seconds]",
            },
            
            'positive_cache_time': {
                'section': 'ca_default',
                'default': '604800',
                'description': 'how long should we cache existing addresses [seconds]',
            },
            
            'negative_cache_time': {
                'section': 'ca_default',
                'default': '14400',
                'description': 'how long should we keep negative cache entries [seconds]',
            },
            
            'server': {
                'section': 'ca_default',
                'default': 'mx:${domain}',
                'description': 'how should we retrieve the next hop?',
            },
            
            'test_fallback': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'if first server fails, try fallback relays?',
            },
            
            'sender': {
                'section': 'ca_default',
                'default': '${bounce}',
                'description': '${bounce}',
            },
            
            'use_tls': {
                'section': 'ca_default',
                'default': 'True',
                'description': 'use opportunistic TLS if supported by server. set to False to disable tls',
            },
            
            'smtp_port' : {
                'section': 'ca_default',
                'default': '25',
                'description': 'check on this TCP port. defaults to 25 (smtp)',
            },
            
            'accept_on_tempfail': {
                'section': 'ca_default',
                'default': 'True',
                'description': 'accept mail on temporary error (4xx) of target server, DEFER otherwise',
            },
    
            'defer_on_hostnotfound': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'defer instead of accept if target server has no A records defined.',
            },
            
            'defer_on_relayaccessdenied': {
                'section': 'ca_default',
                'default': 'False',
                'description': 'defer instead of reject if target server says "Relay access denied"',
            },
            
            'no_valid_server_fail_action': {
                'section': 'ca_default',
                'default': 'DEFER', # you may even want to use REJECT here
                'description': "action if we don't find a server to ask",
            },
            
            'no_valid_server_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a recipient domain if we don't find a server to ask [seconds]",
            },
            
            'no_valid_server_fail_message': {
                'section': 'ca_default',
                'default': '${errormessage}',
                'description': "message template template if we don't find a server to ask",
            },
            
            'resolve_fail_action': {
                'section': 'ca_default',
                'default': 'DEFER',
                'description': "action if we can't resolve target server hostname",
            },
            
            'resolve_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if we can't resolve target server hostname [seconds]",
            },
            
            'resolve_fail_message': {
                'section': 'ca_default',
                'default': '${errormessage}',
                'description': "message template if we can't resolve target server hostname",
            },
            
            'preconnect_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if we encounter a failure before connecting to target server (continue, tempfail, reject)",
            },
            
            'preconnect_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if we encounter a failure before connecting to target server [seconds]",
            },
            
            'preconnect_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if we encounter a failure before connecting to target server",
            },
            
            'connect_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if we cannot connect to the target server (continue, tempfail, reject)",
            },
            
            'connect_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if we cannot connect to the target server [seconds]",
            },
            
            'connect_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if we cannot connect to the target server",
            },

            'helo_name': {
                'section': 'ca_default',
                'default': '',
                'description': "HELO name for smtp test (empty: uses socket.getfqdn(), string: use string directly, string starting with '$' will get environment variable",
            },

            'helo_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if the target server does not accept our HELO (continue, tempfail, reject)",
            },
            
            'helo_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if the target server does not accept our HELO [seconds]",
            },
            
            'helo_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if the target server does not accept our HELO (continue, tempfail, reject)",
            },
            
            'mail_from_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if the target server does not accept our from address",
            },
            
            'mail_from_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if the target server does not accept our from address [seconds]",
            },
            
            'mail_from_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if the target server does not accept our from address",
            },
            
            'rcpt_to_fail_action': {
                'section': 'ca_default',
                'default': 'continue',
                'description': "action if the target server show unexpected behaviour on presenting the recipient address (continue, tempfail, reject)",
            },
            
            'rcpt_to_fail_interval': {
                'section': 'ca_default',
                'default': '3600',
                'description': "how long should we skiplist a server if the target server show unexpected behaviour on presenting the recipient address [seconds]",
            },
            
            'rcpt_to_fail_message': {
                'section': 'ca_default',
                'default': '',
                'description': "message template if the target server show unexpected behaviour on presenting the recipient address",
            },

            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }
    
    
    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True
        if not SQL_EXTENSION_ENABLED:
            print("ERROR: sqlalchemy is not installed")
            return False
        
        if not HAVE_DOMAINMAGIC:
            print('WARNING: domainmagic is not installed - some functionality will not be available')
        
        if not self.checkConfig():
            return False

        if self.config.get('ca_default', 'server').startswith('mx:') and not DNSQUERY_EXTENSION_ENABLED:
            print("ERROR: no DNS resolver library available - required for mx resolution")
            return False
        elif not DNSQUERY_EXTENSION_ENABLED:
            print("WARNING: no DNS resolver library available - some functionality will not be available")
        
        if self.config.get(self.section, 'cache_storage') == 'redis' and not REDIS_ENABLED:
            print('ERROR: redis backend configured but redis python module not available')
            return False
        
        self._init_cache()
        if self.cache is None:
            cache_storage = self.config.get(self.section, 'cache_storage')
            print('ERROR: failed to initialize cache with storage %s' % cache_storage)
            return False
        else:
            ok = self.cache.lint()
            if not ok:
                return False
        
        self._init_config_backend('lintuser@fuglu.org')
        try:
            poscount, negcount = self.cache.get_total_counts()
            print("INFO: Addresscache: %s positive entries, %s negative entries"%(poscount,negcount))
        except Exception as e:
            print("ERROR: DB Connection failed: %s" % str(e))
            return False
        
        test = SMTPTest(self.config)
        try:
            timeout = test.get_domain_config_float('lint', 'timeout')
            #print('Using default config timeout: %ss' % timeout)
        except Exception:
            print('WARNING: Could not get timeout value from config, using internal default of 10s')
            
        try:
            dbconnection = self.config.get(self.section, 'dbconnection')
            conn=get_session(dbconnection)
            conn.execute("SELECT 1")
        except Exception as e:
            print("ERROR: Failed to connect to SQL database: %s" % str(e))
            return False
            
        return True
    
    
    def __str__(self):
        return "Address Check"
    
    
    def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        timetracker = TrackTimings(enable=self.enabletimetracker)
        self.logger.debug(f"{sess.id} timetracker enabled: {self.enabletimetracker}")
        from_address = force_uString(sess.sender)
        if from_address is None:
            self.logger.error(f'{sess.id} No FROM address found')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        # check current recipient
        to_address = force_uString(recipient)
        if to_address is None:
            self.logger.error(f'{sess.id} No TO address found')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        if to_address and to_address.lower() == "postmaster":
            self.logger.info(f'{sess.id} Postmaster TO address found -> skip')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE

        always_accept_regex = self.config.get(self.section, 'always_accept_regex').strip()
        if always_accept_regex and re.match(always_accept_regex, to_address, re.I):
            self.logger.info(f'{sess.id} TO address {to_address} matches always accept regex {always_accept_regex}')
            return sm.CONTINUE
        
        if HAVE_DOMAINMAGIC:
            to_address = strip_batv(to_address)
        
        domain = sm.MilterSession.extract_domain(to_address)
        if domain is None:
            self.logger.error(f'{sess.id} No TO domain in recipient {to_address} found')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE
        
        #check cache
        self._init_cache()
        self._init_config_backend(to_address)
        timetracker.tracktime("init-cache")


        # it's possible to get an error trying to get the cached value therefore
        # 2 attempts are made
        entry = None
        attempts = 2
        while attempts:
            attempts -= 1
            try:
                entry = self.cache.get_address(to_address)
                self.logger.debug(f'{sess.id} Get cached address {to_address} entry: {entry}')
            except Exception as e:
                if attempts:
                    self.logger.warning(f'{sess.id} Could not get cached address {to_address}: {str(e)}')
                else:
                    self.logger.error(f'{sess.id} Could not get cached address {to_address}: {str(e)}')
                    timetracker.report_plugintime(sess.id, str(self))
                    return sm.CONTINUE
        
        timetracker.tracktime("get_address from cache database")
        
        if entry is not None:
            positive, message = entry
            
            if positive:
                self.logger.info(f'{sess.id} accepting cached address {to_address}')
                timetracker.report_plugintime(sess.id, str(self))
                return sm.CONTINUE
            else:
                if self.config.getboolean(self.section,'always_accept'):
                    self.logger.info(f'{sess.id} Learning mode - accepting despite negative cache entry')
                else:
                    self.logger.info(f'{sess.id} rejecting negative cached address {to_address} : {message}')
                    timetracker.report_plugintime(sess.id, str(self))

                    template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
                    templ_dict = sess.get_templ_dict()
                    templ_dict['message'] = message
                    rejectmessage = template.safe_substitute(templ_dict)
                    return sm.REJECT, rejectmessage
        else:
            self.logger.debug(f"{sess.id} Address {to_address} not in database or entry has expired")
        
        #load domain config
        domainconfig = self.config_backend.get_domain_config_all()
        timetracker.tracktime("domainconfig")

        if domainconfig is None:
            self.logger.debug(f'{sess.id} domain config for domain {domain} was empty')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE
        
        #enabled?
        test = SMTPTest(self.config, self.section, self.relaycache)
        servercachetime = test.get_domain_config_int(domain, 'test_server_interval', domainconfig)

        enabled = test.get_domain_config_bool(domain, 'enabled', domainconfig)
        timetracker.tracktime("cachetime-enabled")
        if not enabled:
            self.logger.info(f'{sess.id} {to_address}: call-aheads for domain {domain} are disabled')
            timetracker.report_plugintime(sess.id, str(self))
            return sm.CONTINUE
        
        positive_directory_only = test.get_domain_config_bool(domain, 'positive_directory_only', domainconfig)
        testaddress=test.maketestaddress(domain, domainconfig)
        testentry = self.cache.get_address(testaddress)
        if positive_directory_only and testentry:
            # we require the test user to be present in directory as a safety mesaure
            # if it is not there, db got flushed/corrupted/outdated and user should be accepted
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate_directory_only'))
            templ_dict = sess.get_templ_dict()
            rejectmessage = template.safe_substitute(templ_dict)
            return sm.REJECT, rejectmessage
        
        #check skiplist
        relays=test.get_relays(domain, domainconfig)
        timetracker.tracktime("get_relays")
        result = SMTPTestResult()
        timetracker.tracktime("SMTPTest")
        need_server_test = False
        relay = None
        if relays is None or len(relays)==0:
            self.logger.error(f"{sess.id} no relay for domain {domain} found!")
            result.state=SMTPTestResult.TEST_FAILED
            result.errormessage=f"no relay for domain {domain} found"
        
        if relays is not None:
            try:
                timeout = test.get_domain_config_float(domain, 'timeout', domainconfig)
            except (ValueError, TypeError):
                timeout = 10
            sender = test.get_domain_config(domain, 'sender', domainconfig, {'bounce':'','originalfrom':from_address})
            use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig)
            smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
            
            # only check test address if really needed...
            # the world market leader's good office 365 does not like being hammered with invalid rcpts
            addresses = [to_address]
            if testentry is not None:
                need_server_test = testentry[0]
            else:
                need_server_test = True
            if need_server_test:
                self.logger.info(f'{sess.id} need to test {testaddress}')
                addresses.append(testaddress)
            else:
                self.logger.info(f'{sess.id} skipping test of {testaddress}')
            
            test_relays = relays[:]
            if not test.get_domain_config_bool(domain, 'test_fallback', domainconfig):
                test_relays = relays[:1] # skip all except first relay in list
            
            starttime = time.time()
            for relay in test_relays:
                self.logger.debug(f"{sess.id} testing relay {relay} for domain {domain}")
                if self.cache.is_skiplisted(domain, relay):
                    self.logger.info(f'{sess.id} {to_address}: server {relay} for domain {domain} is skiplisted for call-aheads, skipping')
                    timetracker.report_plugintime(sess.id, str(self))
                    return sm.CONTINUE
                
                #make sure we don't call-ahead ourself
                if to_address==testaddress:
                    self.logger.error(f"{sess.id} call-ahead loop detected!")
                    self.cache.skiplist(domain, relay, servercachetime, SMTPTestResult.STAGE_CONNECT, 'call-ahead loop detected')
                    timetracker.report_plugintime(sess.id, str(self))
                    return sm.CONTINUE
                
                #perform call-ahead
                self.logger.debug(f"Testing relay {relay} for {addresses} from {sender} with timeout {timeout} and tls:{use_tls} at port {smtp_port}")
                result=test.smtptest(relay, addresses, mailfrom=sender, timeout=timeout, use_tls=use_tls, port=smtp_port)
                
                if result.stage == SMTPTestResult.STAGE_RCPT_TO:
                    # this server was tested until rcpt to - it's a functioning smtp relay
                    # we could additionally check if there was a 450 - we ignore that for now
                    break
                    
                if time.time() > starttime + timeout:
                    self.logger.debug(f'{sess.id} skipping further relays - timeout exceeded')
                    break
            timetracker.tracktime("RelayTests")

        
        if result.state != SMTPTestResult.TEST_OK:
            action = sm.CONTINUE
            message = None
            
            for stage in [SMTPTestResult.STAGE_PRECONNECT, SMTPTestResult.STAGE_RESOLVE, SMTPTestResult.STAGE_CONNECT,
                          SMTPTestResult.STAGE_HELO, SMTPTestResult.STAGE_MAIL_FROM, SMTPTestResult.STAGE_RCPT_TO]:
                if result.stage == stage:
                    stageaction, messagetmpl, interval = self._get_stage_config(stage, test, domain, domainconfig,
                                                                                sessid=sess.id)
                    if messagetmpl is None:
                        messagetmpl = ''
                        self.logger.warning(f'{sess.id} message template for stage {stage} not defined')

                    template = _SuspectTemplate(messagetmpl)
                    templ_dict = sess.get_templ_dict()
                    templ_dict['relay'] = relay
                    templ_dict['stage'] = stage
                    templ_dict['errormessage'] = result.errormessage
                    message = template.safe_substitute(templ_dict)

                    if stageaction is not None:
                        action = stageaction
                    if interval is not None:
                        servercachetime = min(servercachetime, interval)
            
            if relay is not None:
                self.logger.warning(f'{sess.id} problem testing recipient verification support on server {relay} : {result.errormessage}. putting on skiplist.')
                self.cache.skiplist(domain, relay, servercachetime, result.stage, result.errormessage)
            timetracker.tracktime("SMTPTestResult.Test_OK-fail")
            timetracker.report_plugintime(sess.id, str(self))
            return action, message
        
        blreason='unknown'
        if need_server_test:
            addrstate,code,msg=result.rcptoreplies[testaddress]
            recverificationsupport=None
            if addrstate==SMTPTestResult.ADDRESS_OK:
                blreason='accepts any recipient'
                recverificationsupport=False
            elif addrstate==SMTPTestResult.ADDRESS_TEMPFAIL:
                blreason='temporary failure: %s %s'%(code,msg)
                recverificationsupport=False
            elif addrstate==SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                recverificationsupport=True
            self.cache.put_address(testaddress, servercachetime, not recverificationsupport, msg)
            timetracker.tracktime("need_server_test")
        else:
            recverificationsupport=True


        #override: ignore recipient verification fail
        if self.config.getboolean(self.section,'always_assume_rec_verification_support'):
            recverificationsupport=True
        
        if recverificationsupport:
            addrstate,code,msg=result.rcptoreplies[to_address]
            positive=True
            cachetime = test.get_domain_config_int(domain, 'positive_cache_time', domainconfig)
            
            #handle case where testadress got 5xx , but actual address got 4xx
            if addrstate==SMTPTestResult.ADDRESS_TEMPFAIL:
                self.logger.info(f'{sess.id} server {relay} for domain {domain}: '
                                 f'skiplisting for {servercachetime} seconds (tempfail: {msg})')
                self.cache.skiplist(domain, relay, servercachetime, result.stage, 'tempfail: %s'%msg)
                timetracker.tracktime("recverificationsupport-tempfail")
                if test.get_domain_config_bool(domain, 'accept_on_tempfail', domainconfig):
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.CONTINUE
                else:
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.TEMPFAIL, msg
            
            defer_on_hostnotfound = test.get_domain_config_bool(domain, 'defer_on_hostnotfound', domainconfig)
            if defer_on_hostnotfound and (msg.endswith('has no A records') or msg.endswith('host name could not be resolved')):
                return sm.TEMPFAIL, msg
            
            defer_on_relayaccessdenied = test.get_domain_config_bool(domain, 'defer_on_relayaccessdenied', domainconfig)
            relayaccessdenied = False
            if addrstate==SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                positive=False
                cachetime = test.get_domain_config_int(domain, 'negative_cache_time', domainconfig)
                
            if 'relay access denied' in msg.lower():
                relayaccessdenied = True
                
            if not (relayaccessdenied and defer_on_relayaccessdenied):
                # don't cache if we defer
                self.cache.put_address(to_address,cachetime,positive,msg)
                neg = ""
                if not positive:
                    neg = "negative "
                self.logger.info(f"{sess.id} {neg}cached {to_address} for {cachetime} seconds ({msg})")

            timetracker.tracktime("recverificationsupport")
            if positive:
                timetracker.report_plugintime(sess.id, str(self), end=False)
                return sm.CONTINUE
            else:
                if self.config.getboolean(self.section,'always_accept'):
                    self.logger.info(f'{sess.id} learning mode - accepting despite inexistent address')
                elif relayaccessdenied and defer_on_relayaccessdenied:
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.TEMPFAIL, msg
                else:
                    timetracker.report_plugintime(sess.id, str(self), end=False)
                    return sm.REJECT, msg
            
        else:
            self.logger.info(f'{sess.id} server {relay} for domain {domain}: '
                             f'skiplisting for {servercachetime} seconds ({blreason}) in stage {result.stage}')
            self.cache.skiplist(domain, relay, servercachetime, result.stage, blreason)
            timetracker.tracktime("no-recverificationsupport")
        timetracker.report_plugintime(sess.id, str(self))
        return sm.CONTINUE

    def _get_stage_config(self, stage, test, domain, domainconfig, sessid: str = "<>"):
        try:
            interval = test.get_domain_config_int(domain, f'{stage}_fail_interval', domainconfig)
        except (ValueError, TypeError):
            interval = None
            self.logger.debug(f'{sessid} Invalid {stage}_fail_interval for domain {domain}')
        stageaction = sm.STR2RETCODE.get(test.get_domain_config(domain, f'{stage}_fail_action', domainconfig), sm.CONTINUE)
        message = test.get_domain_config(domain, f'{stage}_fail_message', domainconfig) or None
        
        return stageaction, message, interval


class SMTPTestResult:
    STAGE_PRECONNECT="preconnect"
    STAGE_RESOLVE="resolve"
    STAGE_CONNECT="connect"
    STAGE_HELO="helo"
    STAGE_MAIL_FROM="mail_from"
    STAGE_RCPT_TO="rcpt_to"
    
    TEST_IN_PROGRESS=0
    TEST_FAILED=1
    TEST_OK=2
    
    ADDRESS_OK=0
    ADDRESS_DOES_NOT_EXIST=1
    ADDRESS_TEMPFAIL=2
    ADDRESS_UNKNOWNSTATE=3
    
    def __init__(self):
        #at what stage did the test end
        self.stage=SMTPTestResult.STAGE_PRECONNECT
        #test ok or error
        self.state=SMTPTestResult.TEST_IN_PROGRESS    
        self.errormessage=None 
        self.relay=None
        
        #replies from smtp server
        #tuple: (code,text)
        self.banner=None
        self.heloreply=None
        self.mailfromreply=None
        
        #address verification
        #tuple: (ADDRESS_STATUS,code,text)
        self.rcptoreplies={}
    
    def __str__(self):
        str_status="in progress"
        if self.state==SMTPTestResult.TEST_FAILED:
            str_status="failed"
        elif self.state==SMTPTestResult.TEST_OK:
            str_status="ok"
        
        str_stage="unknown"    
        stagedesc={
            SMTPTestResult.STAGE_PRECONNECT:"preconnect",
            SMTPTestResult.STAGE_RESOLVE:"resolve",
            SMTPTestResult.STAGE_CONNECT:'connect',
            SMTPTestResult.STAGE_HELO:'helo',
            SMTPTestResult.STAGE_MAIL_FROM:'mail_from',
            SMTPTestResult.STAGE_RCPT_TO:'rcpt_to'
        }
        if self.stage in stagedesc:
            str_stage=stagedesc[self.stage]
            
        desc="TestResult: relay=%s status=%s stage=%s"%(self.relay,str_status,str_stage)
        if self.state==SMTPTestResult.TEST_FAILED:
            desc="%s error=%s"%(desc,self.errormessage)
            return desc
        
        addrstatedesc={
            SMTPTestResult.ADDRESS_DOES_NOT_EXIST:'no',
            SMTPTestResult.ADDRESS_OK:'yes',
            SMTPTestResult.ADDRESS_TEMPFAIL:'no (temp fail)',
            SMTPTestResult.ADDRESS_UNKNOWNSTATE:'unknown'
        }
        
        for k in self.rcptoreplies:
            v=self.rcptoreplies[k]
            statedesc=addrstatedesc[v[0]]
            
            desc="%s\n %s: accepted=%s code=%s (%s)"%(desc,k,statedesc,v[1],v[2])
            
        return desc


class SMTPTest(object):
    def __init__(self, config=None, section=None, relaycache=None):
        self.config = config
        self.section = section
        self.relaycache = relaycache
        self.logger=logging.getLogger('%s.smtptest' % __package__ if __package__ else "fuglu")
        self.be_verbose = False

    def is_ip(self, value):
        return RE_IPV4.match(value) or RE_IPV6.match(value)

    def is_testaddress(self, address):
        domain = address.rsplit('@',1)[-1]
        testaddr = self.maketestaddress(domain)
        return address == testaddr

    def maketestaddress(self, domain, domainconfig=None):
        """
        Return a static test address that probably doesn't exist.
        It is NOT randomly generated, so we can check if the incoming
        connection does not produce a call-ahead loop
        """
        testuser = self.get_domain_config(domain, 'testuser', domainconfig, {'domain': domain})
        return f"{testuser}@{domain}"

    def get_domain_config(self, domain, key, domainconfig=None, templatedict=None):
        """Get configuration value for domain or default. Apply template string if templatedict is not None"""
        defval=self.config.get('ca_default',key)
        
        theval=defval
        if domainconfig is None: #nothing from sql
            #check config file overrides
            configbackend=ConfigFileBackend(self.config, self.section)
            
            #ask the config backend if we have a special server config
            backendoverride=configbackend.get_domain_config_value(key)
            if backendoverride is not None:
                theval=backendoverride
        elif key in domainconfig:
            theval=domainconfig[key]
        
        if templatedict is not None:
            theval=Template(theval).safe_substitute(templatedict) 
        
        return theval

    def get_domain_config_int(self,domain,key,domainconfig=None,templatedict=None):
        value = self.get_domain_config(domain,key,domainconfig,templatedict)
        return int(value)
    
    def get_domain_config_float(self,domain,key,domainconfig=None,templatedict=None):
        value = self.get_domain_config(domain,key,domainconfig,templatedict)
        return float(value)
    
    def get_domain_config_bool(self,domain,key,domainconfig=None,templatedict=None):
        value = self.get_domain_config(domain,key,domainconfig,templatedict)
        value = value.lower()
        if value in ["1", "yes", "true", "on"]:
            return True
        if value in ["0", "no", "false", "off"]:
            return False
        raise ValueError('not a boolean value: %s' % value)

    def get_relays(self, domain, domainconfig=None):
        """Determine the relay(s) for a domain"""
        relays = None
        if self.relaycache is not None:
            relays = self.relaycache.get_cache(domain)
            if relays is not None:
                return relays
    
        serverconfig = self.get_domain_config(domain, 'server', domainconfig, {'domain': domain})
    
        tp, val = serverconfig.split(':', 1)
    
        if tp == 'sql':
            conn = get_session(self.config.get(self.section, 'dbconnection'))
            ret = conn.execute(val)
            relays = []
            for row in ret:
                for item in row:
                    relays.append(item)
            conn.remove()
        elif tp == 'mx':
            relays = mxlookup(val)
        elif tp == 'static':
            relays = [val, ]
        elif tp == 'txt':
            try:
                with open(val) as fp:
                    lines = fp.readlines()
                for line in lines:
                    fdomain, ftarget = line.split()
                    if domain.lower() == fdomain.lower():
                        relays = [ftarget, ]
                        break
            except Exception as e:
                self.logger.error(f"Txt lookup failed: {str(e)}")
        else:
            self.logger.error(f'unknown relay lookup type: {tp}')
    
        if self.relaycache is not None and relays is not None:
            self.relaycache.put_cache(domain, relays)
        return relays

    def smtptest(self,relay,addrlist,helo=None,mailfrom=None,timeout=10, use_tls=1, port=smtplib.SMTP_PORT):
        """perform a smtp check until the rcpt to stage
        returns a SMTPTestResult
        """

        if self.be_verbose:
            logging.getLogger('fuglu.SMTPTester').debug(f"Create SMTPTestResult object")
        result=SMTPTestResult()
        result.relay=relay
        
        if mailfrom is None:
            mailfrom=""

        if helo is None:
            heloinput=self.config.get('ca_default', 'helo_name')
            if heloinput and heloinput.strip():
                heloinput = heloinput.strip()
                if heloinput.startswith('$') and heloinput[1:]:
                    # get from environment variable
                    helo = os.getenv(heloinput[1:], default=None)
                else:
                    helo = heloinput
        if self.be_verbose:
            logging.getLogger('fuglu.SMTPTester').debug(f"helo is: {helo}")

        if self.be_verbose:
            logging.getLogger('fuglu.SMTPTester').debug(f"STAGE_RESOLVE")
        result.stage=SMTPTestResult.STAGE_RESOLVE
        if DNSQUERY_EXTENSION_ENABLED and not self.is_ip(relay):
            arecs = lookup(relay)
            if arecs is None:
                result.state=SMTPTestResult.TEST_FAILED
                result.errormessage=f"relay {relay} host name could not be resolved"
                return result
            elif arecs is not None and len(arecs)==0:
                result.state=SMTPTestResult.TEST_FAILED
                result.errormessage=f"relay {relay} has no A records"
                return result

        if self.be_verbose:
            logging.getLogger('fuglu.SMTPTester').debug(f"STAGE_CONNECT")
        result.stage=SMTPTestResult.STAGE_CONNECT
        smtp=smtplib.SMTP(local_hostname=helo)
        smtp.timeout=timeout
        #smtp.set_debuglevel(True)
        try:
            code,msg=smtp.connect(relay, port)
            result.banner=(code,msg)
            if code<200 or code>299:
                result.state=SMTPTestResult.TEST_FAILED
                result.errormessage=f"relay {relay} did not accept connection: {force_uString(msg)}"
                return result
        except Exception as e:
            result.errormessage=str(e)
            result.state=SMTPTestResult.TEST_FAILED
            if self.be_verbose:
                logging.getLogger('fuglu.SMTPTester').exception(e)
            return result
        
        #HELO
        if self.be_verbose:
            logging.getLogger('fuglu.SMTPTester').debug(f"STAGE_HELO")
        result.stage=SMTPTestResult.STAGE_HELO
        try:
            code, msg = smtp.ehlo()
            result.heloreply=(code,msg)
            if 199 < code < 300:
                if smtp.has_extn('STARTTLS') and use_tls:
                    # according to https://docs.python.org/3/library/ssl.html#ssl-security
                    context = ssl.create_default_context()

                    if not smtp._host:
                        smtp._host = relay

                    # ignore cert errors (like expired certificates, ...)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    code,msg = smtp.starttls(context=context)
                    if 199 < code < 300:
                        code,msg=smtp.ehlo()
                        if code < 200 or code > 299:
                            result.state=SMTPTestResult.TEST_FAILED
                            result.errormessage=f"relay {relay} did not accept EHLO after STARTTLS: {force_uString(msg)}"
                            return result
                    else:
                        self.logger.info(f'relay {relay} did not accept starttls: {code} {force_uString(msg)}')
                else:
                    self.logger.info(f'relay {relay} does not support starttls: {code} {force_uString(msg)}')
            else:
                self.logger.info(f'relay {relay} does not support esmtp, falling back')
                code, msg = smtp.helo()
                if code < 200 or code > 299:
                    result.state = SMTPTestResult.TEST_FAILED
                    result.errormessage = f"relay {relay} did not accept HELO: {force_uString(msg)}"
                    return result
        except Exception as e:
            result.errormessage=str(e)
            result.state=SMTPTestResult.TEST_FAILED
            if self.be_verbose:
                logging.getLogger('fuglu.SMTPTester').exception(e)
            return result
        
        #MAIL FROM
        if self.be_verbose:
            logging.getLogger('fuglu.SMTPTester').debug(f"STAGE_MAIL_FROM")
        result.stage=SMTPTestResult.STAGE_MAIL_FROM
        try:
            code,msg=smtp.mail(mailfrom)
            result.mailfromreply=(code,msg)
            if code<200 or code>299:
                result.state=SMTPTestResult.TEST_FAILED
                result.errormessage="relay %s did not accept MAIL FROM: %s" % (relay, force_uString(msg))
                return result
        except Exception as e:
            result.errormessage=str(e)
            result.state=SMTPTestResult.TEST_FAILED
            if self.be_verbose:
                logging.getLogger('fuglu.SMTPTester').exception(e)
            return result
        
        #RCPT TO
        if self.be_verbose:
            logging.getLogger('fuglu.SMTPTester').debug(f"STAGE_RCPT_TO")
        result.stage=SMTPTestResult.STAGE_RCPT_TO
        try:
            addrstate=SMTPTestResult.ADDRESS_UNKNOWNSTATE
            for addr in addrlist:
                if addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST and self.is_testaddress(addr):
                    # we can skip test address check if real rcpt addr does not exist
                    result.rcptoreplies[addr]=(addrstate,code,'skipped test address check')
                    self.logger.warning('skipped test addres check for %s' % addr)
                    continue
                
                code,msg=smtp.rcpt(addr)
                if 199 < code < 300:
                    addrstate = SMTPTestResult.ADDRESS_OK
                elif 399 > code < 500:
                    addrstate = SMTPTestResult.ADDRESS_TEMPFAIL
                elif 499 < code < 600:
                    addrstate = SMTPTestResult.ADDRESS_DOES_NOT_EXIST
                else:
                    addrstate = SMTPTestResult.ADDRESS_UNKNOWNSTATE
                
                putmsg = f"relay {relay} said: {force_uString(msg)}"
                result.rcptoreplies[addr] = (addrstate,code,putmsg)
        except Exception as e:
            result.errormessage = str(e)
            result.state = SMTPTestResult.TEST_FAILED
            if self.be_verbose:
                logging.getLogger('fuglu.SMTPTester').exception(e)
            return result
        
        result.state=SMTPTestResult.TEST_OK
        
        try:
            smtp.quit()
        except Exception:
            pass
        return result   


class CallAheadCacheInterface(object):
    def __init__(self, config, section):
        self.config=config
        self.section=section
        self.logger=logging.getLogger(f'{__package__ if __package__ else "fuglu"}.ca.{self.__class__.__name__}')
    
    def skiplist(self, domain, relay, expires, failstage=SMTPTestResult.STAGE_RCPT_TO, reason='unknown'):
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        self.logger.error('skiplist:not implemented')
    
    def is_skiplisted(self, domain, relay):
        """Returns True if the server/relay combination is currently skiplisted and should not be used for recipient verification"""
        self.logger.error('is_skiplisted: not implemented')
        return False
    
    def get_skiplist(self):
        """return all skiplisted servers"""
        self.logger.error('get_skiplist: not implemented')
        #expected format per item: domain, relay, reason, expiry timestamp
        return []
    
    def unskiplist(self, relayordomain):
        """remove a server from the skiplist/history"""
        self.logger.error('unskiplist: not implemented')
        return 0
    
    def wipe_domain(self, domain, positive=None):
        self.logger.error('wipe_domain: not implemented')
        return 0
    
    def get_all_addresses(self, domain):
        self.logger.error('get_all_addresses: not implemented')
        return []
    
    def put_address(self, address, expires, positiveEntry=True, message=None):
        """add address to cache"""
        self.logger.error('put_address: not implemented')
    
    def get_address(self, address):
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        self.logger.error('get_address: not implemented')
        return None
    
    def wipe_address(self, address):
        """remove address from cache"""
        self.logger.error('wipe_address: not implemented')
        return 0
    
    def get_total_counts(self):
        self.logger.error('get_total_counts: not implemented')
        return 0, 0
    
    def cleanup(self):
        self.logger.error('cleanup: not implemented')
        return 0, 0, 0
    
    def lint(self):
        self.logger.warning('lint: not implemented')
        return True # we still consider the test to be successful

    
class MySQLCache(CallAheadCacheInterface):
    def __init__(self, config, section):
        CallAheadCacheInterface.__init__(self, config, section)
        self.conn = self.config.get(self.section, 'dbconnection')
    
    def skiplist(self, domain, relay, seconds, failstage='rcpt_to', reason='unknown'):
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        conn=get_session(self.conn)

        statement="""INSERT INTO ca_skiplist (domain,relay,expiry_ts,check_stage,reason)
                    VALUES (:domain,:relay,now()+interval :interval second,:check_stage,:reason)
                    ON DUPLICATE KEY UPDATE expiry_ts=GREATEST(expiry_ts,now()+interval :interval second),check_stage=:check_stage,reason=:reason
                    """
        values={
                'domain':domain,
                'relay':relay,
                'interval':seconds,
                'check_stage':failstage,
                'reason':reason,
                }
        conn.execute(statement,values)
        conn.remove()

    def is_skiplisted(self, domain, relay):
        """Returns True if the server/relay combination is currently skiplisted and should not be used for recipient verification"""
        conn = get_session(self.conn)
        if not conn:
            return False
        statement="SELECT reason FROM ca_skiplist WHERE domain=:domain and relay=:relay and expiry_ts>now()"
        values={'domain':domain,'relay':relay}
        sc=conn.execute(statement, values).scalar()
        conn.remove()
        return sc

    def unskiplist(self, relayordomain):
        """remove a server from the skiplist/history"""
        conn = get_session(self.conn)
        statement="""DELETE FROM ca_skiplist WHERE domain=:removeme or relay=:removeme"""
        values={'removeme':relayordomain}
        res=conn.execute(statement, values)
        rc=res.rowcount
        conn.remove()
        return rc

    def get_skiplist(self):
        """return all skiplisted servers"""
        conn = get_session(self.conn)
        if not conn:
            return None
        statement="SELECT domain,relay,reason,expiry_ts FROM ca_skiplist WHERE expiry_ts>now() ORDER BY domain"
        values={}
        result=conn.execute(statement, values)
        ret=[row for row in result]
        conn.remove()
        return ret
    
    def wipe_address(self, address):
        conn = get_session(self.conn)
        if not conn:
            return None
        statement = """DELETE FROM ca_addresscache WHERE email=:email"""
        values = {'email':address}
        res = conn.execute(statement, values)
        rc = res.rowcount
        conn.remove()
        return rc

    def cleanup(self):
        conn = get_session(self.conn)
        postime = self.config.getint('AddressCheck', 'keep_positive_history_time')
        negtime = self.config.getint('AddressCheck', 'keep_negative_history_time')
        statement = """DELETE FROM ca_addresscache WHERE positive=:pos and expiry_ts<(now() -interval :keeptime day)"""
        
        res = conn.execute(statement,dict(pos=0, keeptime=negtime))
        negcount = res.rowcount
        res = conn.execute(statement,dict(pos=1, keeptime=postime))
        poscount = res.rowcount
        
        res = conn.execute("""DELETE FROM ca_skiplist where expiry_ts<now()""")
        blcount = res.rowcount
        conn.remove()
        return poscount,negcount,blcount
    
    
    def wipe_domain(self, domain, positive=None):
        """wipe all cache info for a domain. 
        if positive is None(default), all cache entries are deleted. 
        if positive is False all negative cache entries are deleted
        if positive is True, all positive cache entries are deleted
        """
        conn = get_session(self.conn)
        if not conn:
            return None
        
        posstatement=""
        if positive is True:
            posstatement = "and positive=1"
        if positive is False:
            posstatement = "and positive=0"
        
        statement="""DELETE FROM ca_addresscache WHERE domain=:domain %s"""%posstatement
        values={'domain':domain}
        res=conn.execute(statement, values)
        rc= res.rowcount
        conn.remove()
        return rc
    
    def put_address(self, address, seconds, positiveEntry=True, message=None):
        """put address into the cache"""
        conn = get_session(self.conn)
        if not conn:
            return None
        statement="""INSERT INTO ca_addresscache (email,domain,expiry_ts,positive,message) VALUES (:email,:domain,now()+interval :interval second,:positive,:message)
        ON DUPLICATE KEY UPDATE check_ts=now(),expiry_ts=GREATEST(expiry_ts,now()+interval :interval second),positive=:positive,message=:message
        """
        domain = sm.MilterSession.extract_domain(address)
        values={'email': address,
                'domain': domain,
                'interval': seconds,
                'positive': positiveEntry,
                'message': message,
            }
        conn.execute(statement, values)
        conn.remove()

    def get_address(self,address):
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        conn = get_session(self.conn)
        if not conn:
            return None
        statement = "SELECT positive,message FROM ca_addresscache WHERE email=:email and expiry_ts>now()"
        values = {'email': address}
        res = conn.execute(statement, values)
        first = res.first()
        conn.remove()
        return first

    def get_all_addresses(self, domain):
        conn = get_session(self.conn)
        if not conn:
            return None
        statement = "SELECT email,positive FROM ca_addresscache WHERE domain=:domain and expiry_ts>now() ORDER BY email"
        values={'domain': domain}
        result=conn.execute(statement, values)
        ret=[x for x in result]
        conn.remove()
        return ret
    
    
    def get_total_counts(self):
        conn = get_session(self.conn)
        statement="SELECT count(*) FROM ca_addresscache WHERE expiry_ts>now() and positive=1"
        result=conn.execute(statement)
        poscount=result.fetchone()[0]
        statement="SELECT count(*) FROM ca_addresscache WHERE expiry_ts>now() and positive=0"
        result=conn.execute(statement)
        negcount=result.fetchone()[0]
        conn.remove()
        return poscount, negcount
    
    
    def lint(self):
        try:
            conn = get_session(self.conn)
            conn.execute('SELECT 1')
            return True
        except Exception as e:
            print(f'Failed to connect to database: {str(e)}')
            return False
     
    
class RedisCache(CallAheadCacheInterface):
    def __init__(self, config, section):
        CallAheadCacheInterface.__init__(self, config, section)
        self.logger = logging.getLogger("fuglu.call-ahead.RedisCache")
        
        redis_url = config.get(self.section, 'redis_conn')
        timeout = self.config.getint(self.section, 'redis_timeout')
        password = self.config.get(self.section, 'redis_password') or None
        self.redis_pool = RedisPooledConn(redis_url, password=password, socket_keepalive=True, socket_timeout=timeout)

    def _update(self, name, values, ttl):
        """atomic update of hash value and ttl in redis"""
        redisconn = self.redis_pool.get_conn()
        pipe = redisconn.pipeline()
        if REDIS2:
            pipe.hmset(name, values)
        else:
            nobools = {}
            for k,v in values.items():
                if isinstance(v, bool):
                    nobools[k] = str(v)
                else:
                    nobools[k] = v
            #pipe.hset(name, mapping=nobools)
            pipe.hmset(name, nobools)
        pipe.expire(name, ttl)
        pipe.execute()

    def _multiget(self, names, keys):
        """atomically gets multiple hashes from redis"""
        redisconn = self.redis_pool.get_conn()
        pipe = redisconn.pipeline()
        for name in names:
            pipe.hmget(name, keys)
        items = pipe.execute()
        self.logger.debug(f"Got {items} for names:{names} and keys:{keys}")
        return items

    def _keys(self, match='*'):
        redisconn = self.redis_pool.get_conn()
        resulting_keys = [key for key in redisconn.scan_iter(match=match, count=250)]
        self.logger.debug(f"Got {resulting_keys} for match {match}")
        return resulting_keys

    def __pos2bool(self, entry, idx):
        """converts string boolean value in list back to boolean"""
        if entry is None or len(entry)<idx:
            pass
        value = force_uString(entry[idx])
        if value == 'True':
            entry[idx] = True
        elif value == 'False':
            entry[idx] = False

    def skiplist(self, domain, relay, expires, failstage=SMTPTestResult.STAGE_RCPT_TO, reason='unknown'):
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        domain = domain.lower()
        name = f'relay-{relay}-{domain}'
        values = {
            'domain': domain,
            'relay': relay.lower(),
            'check_stage': failstage,
            'reason': reason,
            'check_ts': datetime.now().strftime(DATEFORMAT),
        }
        redisconn = self.redis_pool.get_conn()
        expires = max(expires, redisconn.ttl(name))
        self._update(name, values, expires)

    def unskiplist(self, relayordomain):
        """remove a server from the skiplist/history"""
        names = self._keys(f'relay-*{relayordomain.lower()}*')
        if names:
            redisconn = self.redis_pool.get_conn()
            delcount = redisconn.delete(*names)
        else:
            delcount = 0
        return delcount
        
    def is_skiplisted(self, domain, relay):
        """Returns True if the server/relay combination is currently skiplisted and should not be used for recipient verification"""
        name = f'relay-{relay.lower()}-{domain.lower()}'
        redisconn = self.redis_pool.get_conn()
        skiplisted = redisconn.exists(name)
        return skiplisted

    def get_skiplist(self):
        """return all skiplisted servers"""
        names = self._keys('relay-*')
        items = []
        for name in names:
            redisconn = self.redis_pool.get_conn()
            item = redisconn.hmget(name, ['domain', 'relay', 'reason'])
            ttl = redisconn.ttl(name)
            ts = datetime.now() + timedelta(seconds=ttl)
            for idx in range(0,3):
                item[idx] = force_uString(item[idx])
            item.append(ts.strftime(DATEFORMAT))
            items.append(item)
        items.sort(key=lambda x:x[0])
        return items

    def wipe_domain(self, domain, positive=None):
        """remove all addresses in given domain from cache"""
        if positive is not None:
            positive = positive.lower()
        names = self._keys(f'addr-*@{domain.lower()}')
        
        if positive is None or positive == 'all':
            delkeys = names
        else:
            entries = self._multiget(names, ['address', 'positive'])
            delkeys = []
            for item in entries:
                if positive == 'positive' and item[1] == 'True':
                    delkeys.append(f'addr-{item["address"]}')
                elif positive == 'negative' and item[1] == 'False':
                    delkeys.append(f'addr-{item["address"]}')
            
        if delkeys:
            redisconn = self.redis_pool.get_conn()
            delcount = redisconn.delete(*delkeys)
        else:
            delcount = 0
        return delcount

    def get_all_addresses(self, domain):
        """get all addresses in given domain from cache"""
        names = self._keys(f'addr-*@{domain}')
        entries = self._multiget(names, ['address', 'positive'])
        for item in entries:
            self.__pos2bool(item, 1)
            item[0] = force_uString(item[0])
        return entries

    def put_address(self, address, expires, positiveEntry=True, message=None):
        """put address in cache"""
        address = address.lower()
        name = 'addr-%s' % address
        domain = sm.MilterSession.extract_domain(address)
        values = {
            'address': address,
            'domain': domain,
            'positive': positiveEntry,
            'message': message,
            'check_ts': datetime.now().strftime(DATEFORMAT),
        }
        redisconn = self.redis_pool.get_conn()
        expires = max(expires, redisconn.ttl(name))
        self._update(name, values, expires)
        
    
    def get_address(self,address):
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        name = 'addr-%s' % address.lower()
        redisconn = self.redis_pool.get_conn()
        entry = redisconn.hmget(name, ['positive', 'message'])
        if entry[0] is not None:
            self.__pos2bool(entry, 0)
        else:
            entry = None
        
        if entry is not None and entry[1] is not None:
            entry[1] = force_uString(entry[1])
        return entry
        
        
    def wipe_address(self,address):
        """remove given address from cache"""
        name = self._keys('addr-%s' % address.lower())
        redisconn = self.redis_pool.get_conn()
        delcount = redisconn.delete(name)
        return delcount
    
    
    def get_total_counts(self):
        """return how many positive and negative entries are in cache"""
        names = self._keys('addr-*')
        entries = self._multiget(names, ['positive'])
        poscount = negcount = 0
        for item in entries:
            if force_uString(item[0]) == 'True':
                poscount += 1
            else:
                negcount += 1
        return poscount, negcount
    
    
    def cleanup(self):
        # nothing to do on redis
        return 0, 0, 0
    
    
    def lint(self):
        reply = self.redis_pool.check_connection()
        if not reply:
            print('Failed to connect to Redis DB')
        return reply



class MemoryCache(CallAheadCacheInterface):
    def __init__(self,config, section):
        CallAheadCacheInterface.__init__(self, config, section)
        self.cleanupinterval = self.config.getint(self.section, 'cleanupinterval')
        self.cache={} # it would probably be faster to have two local caches, one for relays and one for addresses
        self.lock=threading.Lock()
        
        t = threading.Thread(target=self._clear_cache_thread)
        t.daemon = True
        t.start()
        


    def _clear_cache_thread(self):
        while True:
            time.sleep(self.cleanupinterval)
            now = time.time()
            gotlock = self.lock.acquire(True)
            if not gotlock:
                continue
            
            cleancount = 0
            
            for key in self.cache.keys()[:]:
                obj, exptime = self.cache[key]
                if now > exptime:
                    del self.cache[key]
                    cleancount += 1
            self.lock.release()
            self.logger.debug("Cleaned %s expired entries." % cleancount)
            
            
            
    def _put(self, key, obj, exp):
        now = time.time()
        expiration = now + exp
        
        gotlock=self.lock.acquire(True)
        if gotlock:
            if key in self.cache:
                exptime = self.cache[key][1]
                expiration = max(expiration, exptime)
            self.cache[key] = (obj, expiration)
            self.lock.release()
            
            
            
    def _get(self, key):
        obj, exptime = self.cache.get(key, (None, 0))
        if obj is not None:
            now = time.time()
            if now < exptime:
                obj = None
        return obj
    
    
    
    def skiplist(self,domain,relay,expires,failstage=SMTPTestResult.STAGE_RCPT_TO,reason='unknown'):
        """Put a domain/relay combination on the recipient verification skiplist for a certain amount of time"""
        name = 'relay-%s-%s' % (relay, domain)
        values = {
            'domain': domain,
            'relay': relay,
            'check_stage': failstage,
            'reason': reason,
            'check_ts': datetime.now().strftime(DATEFORMAT),
        }
        self._put(name, values, expires)
        
        
    
    def is_skiplisted(self,domain,relay):
        """Returns True if the server/relay combination is currently skiplisted and should not be used for recipient verification"""
        name = 'relay-%s-%s' % (relay, domain)
        if self._get(name) is not None:
            return True
        else:
            return False
        
        
    
    def get_skiplist(self):
        """return all skiplisted servers"""
        #expected format per item: domain, relay, reason, expiry timestamp
        items = []
        gotlock=self.lock.acquire(True)
        if gotlock:
            now = time.time()
            for name in self.cache.keys():
                if name.startswith('relay-'):
                    obj, exptime = self.cache.get(name)
                    if now < exptime:
                        item = [obj.get('domain'), obj.get('relay'), obj.get('reason'), exptime.strftime(DATEFORMAT)]
                        items.append(item)
            items.sort(key=lambda x: x[0])
            self.lock.release()
        return items
    
    
    
    def unskiplist(self,relayordomain):
        """remove a server from the skiplist/history"""
        delcount = 0
        gotlock=self.lock.acquire(True)
        if gotlock:
            for name in self.cache.keys()[:]:
                if name.startswith('relay-') and relayordomain in name:
                    del self.cache[name]
                    delcount += 1
            self.lock.release()
        return delcount
    
    
    
    def wipe_domain(self,domain,positive=None):
        delcount = 0
        
        if positive is not None:
            positive = positive.lower()
        if positive is None or positive == 'all':
            delall = True
        else:
            delall = False
        
        gotlock=self.lock.acquire(True)
        if gotlock:
            for name in self.cache.keys()[:]:
                if name.startswith('addr-') and name.endswith('-%s'%domain):
                    if delall:
                        del self.cache[name]
                        delcount += 1
                    else:
                        obj, exptime = self.cache[name]
                        if obj.get('positive') and positive == 'positive':
                            del self.cache[name]
                            delcount += 1
                        elif not obj.get('positive') and positive == 'negative':
                            del self.cache[name]
                            delcount += 1
            self.lock.release()
            
        return delcount
    
    
    
    def get_all_addresses(self,domain):
        entries = []
        gotlock=self.lock.acquire(True)
        if gotlock:
            now = time.time()
            for name in self.cache.keys()[:]:
                if name.startswith('addr-') and name.endswith('@%s'%domain):
                    obj, exptime = self.cache.get(name, (None, 0))
                    if now < exptime:
                        entries.append((obj.get('address'), obj.get('positive')))
            self.lock.release()
        return entries
    
    
    
    def put_address(self,address,expires,positiveEntry=True,message=None):
        """add address to cache"""
        name = 'addr-%s' % address
        domain = sm.MilterSession.extract_domain(address)
        values={
            'address':address,
            'domain':domain,
            'positive':positiveEntry,
            'message':message,
            'check_ts':datetime.now().strftime(DATEFORMAT),
        }
        self._put(name, values, expires)
    
    
    
    def get_address(self,address):
        """Returns a tuple (positive(boolean),message) if a cache entry exists, None otherwise"""
        obj = self._get('addr-%s' % address)
        if obj:
            entry = (obj.get('positive'), obj.get('message'))
        else:
            entry = None
        return entry
    
    
    
    def wipe_address(self,address):
        """remove address from cache"""
        delcount = 0
        gotlock=self.lock.acquire(True)
        if gotlock:
            name = 'addr-%s' % address
            if name in self.cache:
                del self.cache[name]
                delcount = 1
            self.lock.release()
        return delcount
    
    
    
    def get_total_counts(self):
        poscount = negcount = 0
        gotlock=self.lock.acquire(True)
        if gotlock:
            now = time.time()
            for name in self.cache.keys():
                obj, exptime = self.cache.get(name)
                if now < exptime:
                    if obj.get('positive'):
                        poscount += 1
                    else:
                        negcount += 1
            self.lock.release()
        return poscount, negcount
    
    
    
    def cleanup(self):
        # nothing to do in memcache
        return 0, 0, 0
    
    
    def lint(self):
        return True
        
 
    
class ConfigBackendInterface(object):
    def __init__(self, config, section):
        self.logger = logging.getLogger('%s.ca.%s' % (__package__ if __package__ else "fuglu", self.__class__.__name__))
        self.config = config
        self.section = section
        self.domain = None
        
    def set_rcpt(self, recipient):
        domain = recipient.rsplit('@', 1)[-1]
        self.domain = domain
    
    def get_domain_config_value(self, key):
        """return a single config value for this domain"""
        self.logger.error("get_domain_config_value: not implemented")
        return None
    
    def get_domain_config_all(self):
        """return all config values for this domain"""
        self.logger.error("get_domain_config_value: not implemented")
        return {}



class DBConfigBackend(ConfigBackendInterface):
    def set_rcpt(self, recipient):
        self.config = DBConfig(self.config, None)
        self.config.set_rcpt(recipient)
        
    def get_domain_config_value(self, key):
        return self.config.get(self.section, key)
    
    def get_domain_config_all(self):
        retval = {}
        self.config.load_section(self.section)
        data = self.config.sectioncache[self.section]
        for row in data:
            retval[row[0]] = row[1]
        return retval



class MySQLConfigBackend(ConfigBackendInterface):
    def __init__(self, config, section):
        ConfigBackendInterface.__init__(self, config, section)
    
    
    def get_domain_config_value(self, key):
        sc=None
        try:
            conn=get_session(self.config.get(self.section, 'dbconnection'))
            res=conn.execute("SELECT confvalue FROM ca_configoverride WHERE domain=:domain and confkey=:confkey", {'domain':self.domain,'confkey':key})
            sc=res.scalar()
            conn.remove()
        except Exception as e:
            self.logger.error(f'Could not connect to config SQL database: {str(e)}')
        return sc
    
    
    def get_domain_config_all(self):
        retval={}
        try:
            conn=get_session(self.config.get(self.section, 'dbconnection'))
            res=conn.execute("SELECT confkey,confvalue FROM ca_configoverride WHERE domain=:domain", {'domain':self.domain})
            for row in res:
                retval[row[0]]=row[1]
            conn.remove()
        except Exception as e:
            self.logger.error(f'Could not connect to config SQL database: {str(e)}')
        return retval



class ConfigFileBackend(ConfigBackendInterface):
    """Read domain overrides directly from config, using ca_<domain> sections"""
    def __init__(self, config, section):
        ConfigBackendInterface.__init__(self, config, section)
    
    
    def get_domain_config_value(self, key):
        if self.config.has_option('ca_%s' % self.domain, key):
            return self.config.get('ca_%s' % self.domain, key)
        return None
    
    
    def get_domain_config_all(self):
        retval = {}
        section = 'ca_%s' % self.domain
        for option in self.config.options(section):
            retval[option]=self.config.get(section, option)
        return retval
        


class SMTPTestCommandLineInterface(BackendMixin):
    def __init__(self):
        super().__init__(None, None)
        self.section = 'AddressCheck'
        
        self.commandlist={
            'put-address':self.put_address,
            'wipe-address':self.wipe_address,
            'wipe-domain':self.wipe_domain,
            'cleanup':self.cleanup,
            'test-dry':self.test_dry,
            'test-config':self.test_config,
            'update':self.update,
            'help':self.help,
            'show-domain':self.show_domain,
            'devshell':self.devshell,
            'show-skiplist':self.show_skiplist,
            'unskiplist':self.unskiplist,
        }
    
    
    
    def cleanup(self,*args):
        config=get_config()
        self._init_cache(config, self.section)
        poscount, negcount, blcount = self.cache.cleanup()
        if 'verbose' in args:
            print("Removed %s positive,%s negative records from history data"%(poscount,negcount))
            print("Removed %s expired relays from call-ahead skiplist"%blcount)
    
    
    
    def devshell(self):
        """Drop into a python shell for debugging"""
        # noinspection PyUnresolvedReferences,PyCompatibility
        import readline
        import code
        logging.basicConfig(level=logging.DEBUG)
        cli=self
        config=get_config('../../../conf/fuglu.conf.dist', '../../../conf/conf.d')
        config.read('../../../conf/conf.d/call-ahead.conf.dist')
        self._init_cache(config, self.section)
        plugin=AddressCheck(config)
        print("cli : Command line interface class")
        print("sqlcache : SQL cache backend")
        print("plugin: AddressCheck Plugin")
        terp=code.InteractiveConsole(locals())
        terp.interact("")
    
    
    
    def help(self,*args):
        myself=sys.argv[0]
        print("usage:")
        print("%s <command> [args]"%myself)
        print("")
        print("Available commands:")
        commands=[
            ("test-dry","<server> <emailaddress> [<emailaddress>] [<emailaddress>]","test recipients on target server using the null-sender, does not use any config or caching data"),
            ("test-config","<emailaddress>","test configuration using targetaddress <emailaddress>. shows relay lookup and target server information"),
            ("update","<emailaddress>","test & update server state&address cache for <emailaddress>"),
            ("put-address","<emailaddress> <positive|negative> <ttl> <message>","add <emailaddress> to the cache"),
            ("wipe-address","<emailaddress>","remove <emailaddress> from the cache/history"),
            ("wipe-domain","<domain> [positive|negative|all (default)]","remove positive/negative/all entries for domain <domain> from the cache/history"),
            ("show-domain","<domain>","list all cache entries for domain <domain>"),
            ("show-skiplist","","display all servers currently skiplisted for call-aheads"),
            ("unskiplist","<relay or domain>","remove relay from the call-ahead skiplist"),
            ("cleanup","[verbose]","clean history data from database. this can be run from cron. add 'verbose' to see how many records where cleared"),
        ]
        for cmd,arg,desc in commands:
            self._print_help(cmd, arg, desc)
    
    def _print_help(self,command,args,description):
        from fuglu.funkyconsole import FunkyConsole
        fc=FunkyConsole()
        bold=fc.MODE['bold']
        cyan=fc.FG['cyan']
        print("%s %s\t%s"%(fc.strcolor(command, [bold,]),fc.strcolor(args,[cyan,]),description))
        
    def performcommand(self):
        args=sys.argv
        if len(args)<2:
            print("no command given.")
            self.help()
            sys.exit(1)
            
        cmd=args[1]
        cmdargs=args[2:]
        if cmd not in self.commandlist:
            print("command '%s' not implemented. try ./call-ahead help"%cmd)
            sys.exit(1)
        
        self.commandlist[cmd](*cmdargs)

    def test_dry(self,*args):
        if len(args)<2:
            print("usage: test-dry <server> <address> [...<address>]")
            sys.exit(1)
        server=args[0]
        addrs=args[1:]
        test=SMTPTest()
        
        domain = sm.MilterSession.extract_domain(addrs[0])
        try:
            config=get_config()
            test.config = config
            self._init_config_backend(addrs[0], config, self.section)
            domainconfig=self.config_backend.get_domain_config_all()
            try:
                timeout = test.get_domain_config_float(domain, 'timeout', domainconfig)
            except (ValueError, TypeError):
                timeout = 10
            use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig)
            smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
        except IOError as e:
            print(str(e))
            timeout = 10
            use_tls=1
            smtp_port = smtplib.SMTP_PORT
        
        result=test.smtptest(server,addrs,timeout=timeout, use_tls=use_tls, port=smtp_port)
        print(result)
    
    
    def test_config(self,*args):
        logging.basicConfig(level=logging.INFO)
        if len(args)!=1:
            print("usage: test-config <address>")
            sys.exit(1)
        address=args[0]
        
        domain = sm.MilterSession.extract_domain(address)

        config=get_config()
        self._init_config_backend(address, config, self.section)
        domainconfig = self.config_backend.get_domain_config_all()
        
        print("Checking address cache...")
        self._init_cache(config, self.section)
        entry=self.cache.get_address(address)
        if entry is not None:
            positive, message = entry
            tp="negative"
            if positive:
                tp="positive"
            print("We have %s cache entry for %s: %s"%(tp,address,message))
        else:
            print("No cache entry for %s"%address)
        
        test=SMTPTest(config, self.section)
        relays=test.get_relays(domain,domainconfig) # type: list
        if relays is None:
            print("No relay for domain %s found!"%domain)
            sys.exit(1)
        print("Relays for domain %s are %s"%(domain,relays))
        for relay in relays:
            print("Testing relay %s" % relay)
            if self.cache.is_skiplisted(domain, relay):
                print("%s is currently skiplisted for call-aheads"%relay)
            else:
                print("%s not skiplisted for call-aheads"%relay)
            
            print("Checking if server supports verification....")
            
            sender=test.get_domain_config(domain, 'sender', domainconfig, {'bounce':'','originalfrom':''})
            testaddress=test.maketestaddress(domain, domainconfig)
            try:
                timeout = test.get_domain_config_float(domain, 'timeout', domainconfig)
            except (ValueError, TypeError):
                timeout = 10
            use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig)
            smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
            result=test.smtptest(relay,[address,testaddress],mailfrom=sender, timeout=timeout, use_tls=use_tls, port=smtp_port)
            if result.state!=SMTPTestResult.TEST_OK:
                print("There was a problem testing this server:")
                print(result)
                continue
                
            
            addrstate,code,msg=result.rcptoreplies[testaddress]
            if addrstate==SMTPTestResult.ADDRESS_OK:
                print("Server accepts any recipient")
            elif addrstate==SMTPTestResult.ADDRESS_TEMPFAIL:
                print("Temporary problem / greylisting detected")
            elif addrstate==SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                print("Server supports recipient verification")
            
            print(result)
    
    
    def put_address(self,*args):
        if len(args)<4:
            print("usage: put-address <emailaddress> <positive|negative> <ttl> <message>")
            sys.exit(1)
            
        address=args[0]
        
        strpos=args[1].lower()
        assert strpos in ['positive','negative'],"Additional argument must be 'positive' or 'negative'"
        if strpos=='positive':
            pos=True
        else:
            pos=False
        
        try:
            ttl = int(args[2])
        except (ValueError, TypeError):
            print('ttl must be an integer')
            sys.exit(1)
            
        message = ' '.join(args[3:])
                
        config = get_config()
        self._init_cache(config, self.section)
        self.cache.put_address(address, ttl, pos, message)
        
    def wipe_address(self,*args):
        if len(args)!=1:
            print("usage: wipe-address <address>")
            sys.exit(1)
        config = get_config()
        self._init_cache(config, self.section)
        rowcount = self.cache.wipe_address(args[0])
        print("Wiped %s records"%rowcount)
    
    def wipe_domain(self,*args):
        if len(args) < 1:
            print("usage: wipe-domain <domain> [positive|negative|all (default)]")
            sys.exit(1)
        
        domain=args[0]

        pos=None
        strpos='' 
        if len(args) > 1:
            strpos=args[1].lower()
            assert strpos in ['positive','negative','all'],"Additional argument must be 'positive', 'negative' or 'all'"
            if strpos=='positive':
                pos=True
            elif strpos=='negative':
                pos=False
            else:
                pos=None
                strpos=''
            
        config = get_config()
        self._init_cache(config, self.section)
        rowcount = self.cache.wipe_domain(domain,pos)
        print("Wiped %s %s records"%(rowcount,strpos))
    
    
    def show_domain(self,*args):
        if len(args) != 1:
            print("usage: show-domain <domain>")
            sys.exit(1)
        config=get_config()
        self._init_cache(config, self.section)
        domain=args[0]
        rows = self.cache.get_all_addresses(domain) # type: list
        
        print("Cache for domain %s (-: negative entry, +: positive entry)"%domain)
        for row in rows:
            email,positive = row
            if positive:
                print("+ %s" % email)
            else:
                print("- %s" % email)
        total=len(rows)
        print("Total %s cache entries for domain %s"%(total,domain))
    
    
    def show_skiplist(self,*args):
        if len(args) > 0:
            print("usage: show-blackist")
            sys.exit(1)
        config = get_config()
        self._init_cache(config, self.section)
        rows = self.cache.get_skiplist() # type: list
        
        print("Call-ahead skiplist (domain/relay/reason/expiry):")
        for row in rows:
            domain,relay,reason,exp=row
            print("%s\t%s\t%s\t%s"%(domain,relay,reason,exp))
            
        total=len(rows)
        print("Total %s skiplisted relays"%total)
    
    
    def unskiplist(self,*args):
        if len(args) < 1:
            print("usage: unskiplist <relay or domain>")
            sys.exit(1)
        relay = args[0]
        config = get_config()
        self._init_cache(config, self.section)
        count = self.cache.unskiplist(relay)
        print("%s entries removed from call-ahead skiplist"%count)
    
    
    def update(self,*args):
        logging.basicConfig(level=logging.INFO)
        if len(args) != 1:
            print("usage: update <address>")
            sys.exit(1)
        address = args[0]
        
        domain = sm.MilterSession.extract_domain(address)

        config = get_config()
        self._init_cache(config, self.section)
        self._init_config_backend(address, config, self.section)
        domainconfig = self.config_backend.get_domain_config_all()

        test = SMTPTest(config)
        relays = test.get_relays(domain,domainconfig)
        if relays is None:
            print("No relay for domain %s found!" % domain)
            sys.exit(1)
        print("Relays for domain %s are %s" % (domain, relays))
        
        relay = relays[0]
        sender = test.get_domain_config(domain, 'sender', domainconfig, {'bounce':'','originalfrom':''})
        testaddress = test.maketestaddress(domain, domainconfig)
        try:
            timeout = test.get_domain_config_float(domain, 'timeout', domainconfig)
        except (ValueError, TypeError):
            timeout = 10
        use_tls = test.get_domain_config_bool(domain, 'use_tls', domainconfig)
        smtp_port = test.get_domain_config_int(domain, 'smtp_port', domainconfig)
        result=test.smtptest(relay, [address,testaddress], mailfrom=sender, timeout=timeout, use_tls=use_tls, port=smtp_port)
        
        servercachetime = test.get_domain_config_int(domain, 'test_server_interval', domainconfig)
        if result.state != SMTPTestResult.TEST_OK:
            print("There was a problem testing this server:")
            print(result)
            print("putting server on skiplist")
            self.cache.skiplist(domain, relay, servercachetime, result.stage, result.errormessage)
            return sm.CONTINUE, None
    
    
        addrstate, code, msg = result.rcptoreplies[testaddress]
        recverificationsupport = None
        if addrstate == SMTPTestResult.ADDRESS_OK:
            recverificationsupport=False
        elif addrstate == SMTPTestResult.ADDRESS_TEMPFAIL:
            recverificationsupport=False
        elif addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
            recverificationsupport=True
        
        if recverificationsupport:
            
            if self.cache.is_skiplisted(domain, relay):
                print("Server was skiplisted - removing from skiplist")
                self.cache.unskiplist(relay)
                self.cache.unskiplist(domain)
            
            addrstate, code, msg = result.rcptoreplies[address]
            if addrstate == SMTPTestResult.ADDRESS_DOES_NOT_EXIST:
                positive = False
                cachetime = test.get_domain_config_int(domain, 'negative_cache_time', domainconfig)
            else:
                positive = True
                cachetime = test.get_domain_config_int(domain, 'positive_cache_time', domainconfig)
            
            self.cache.put_address(address, cachetime, positive, msg)
            neg = ""
            if not positive:
                neg = "negative"
            print(f"{neg} cached {address} for {cachetime} seconds")
        else:
            print("Server accepts any recipient")
            if config.getboolean('AddressCheck','always_assume_rec_verification_support'):
                print("skiplistings disabled in config- not skiplisting")
            else:
                self.cache.skiplist(domain, relay, servercachetime, result.stage, 'accepts any recipient')
                print("Server skiplisted")
            

# Usage for checks/debugging (you might have to change location of plugin
# for your installation
#
# get help
# > python /path/to/plugin/call-ahead.py
# apply command
# > python /path/to/plugin/call-ahead.py test-config aaa@aaa.aa
if __name__ == '__main__':
    logging.basicConfig()  
    cli=SMTPTestCommandLineInterface()
    cli.performcommand()