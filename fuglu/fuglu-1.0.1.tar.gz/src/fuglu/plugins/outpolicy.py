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
import os
import logging
import threading
import time
import typing as tp
from string import Template
import random
import re
from email import message_from_bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from domainmagic.mailaddr import strip_batv, decode_srs, email_normalise_ebl
from fuglu.shared import strip_address, extract_domain, FileList, ScannerPlugin, DUNNO, apply_template, \
    string_to_actioncode, actioncode_to_string, get_outgoing_helo
from fuglu.bounce import Bounce
from fuglu.stringencode import force_uString
from fuglu.extensions.sql import get_session, text, SQL_EXTENSION_ENABLED
from fuglu.extensions.redisext import redis, ENABLED as REDIS_ENABLED
from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin
from fuglu.lib.patchedemail import PatchedMessage
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.logtools import createPIDinfo
from .fuzor import FuzorMixin, FuzorDigest
try:
    from pfqd.qstore import QStore
    from pfqd.qtools import queue_size, COL_FROM_DOM, COL_FROM_ADDR
    PFQD_AVAILABLE = True
except ImportError:
    PFQD_AVAILABLE = False


def get_login_from_suspect(suspect, sasl_hdr=None):
    login = suspect.sasl_login
    if login is None and sasl_hdr is not None:
        login = suspect.get_message_rep().get(sasl_hdr)
    return login


class SenderDomainRulesCache(object):
    def __init__(self, dbconnection = None, refreshtime = 300):
        self._dbconnection = dbconnection
        self.refreshtime = refreshtime
        self.logger = logging.getLogger('fuglu.outpolicy.%s' % self.__class__.__name__)
        self.spoofing_cache = {}
        self.bounces_cache = {}
        self.domain_cache = {}
        self.lock = threading.Lock()
        if self._dbconnection is not None:
            self.logger.debug('db for refresh: %s' % self._dbconnection)
            self._refreshcache()
        else:
            self.logger.debug('no db connection')
        t = threading.Thread(target=self.reloadthread)
        t.daemon = True
        t.start()
    
    
    @property
    def dbconnection(self):
        return self._dbconnection
    
    
    @dbconnection.setter
    def dbconnection(self, dbconnection):
        if dbconnection is not None and self._dbconnection != dbconnection:
            self._dbconnection = dbconnection
            self._refreshcache()
    
    
    def reloadthread(self):
        self.logger.info('Reloader thread started. Reloading every %s seconds'%self.refreshtime)
        while True:
            time.sleep(self.refreshtime)
            if self.dbconnection is not None:
                self._refreshcache()
    
    
    def _refreshcache(self, attempts=3):
        self.logger.debug(f"Call refreshcache for {createPIDinfo()}")
        while attempts:
            attempts -= 1
            conn = None
            try:
                self.lock.acquire()
                try:
                    #conn = get_session(self.dbconnection)


                    conn = get_session(self.dbconnection)
                    query = 'SELECT account_name, allow_spoofing, allow_bounces FROM relay_account'
                    result = conn.execute(text(query))
                    accounts = result.fetchall()
                    spoofing_cache = {}
                    spoofing_count = 0
                    bounces_cache = {}
                    bounces_count = 0
                    for line in accounts:
                        key = line['account_name']
                        spoofing_cache[key] = bool(line['allow_spoofing'])
                        if spoofing_cache[key]:
                            spoofing_count += 1
                        bounces_cache[key] = bool(line['allow_bounces'])
                        if bounces_cache[key]:
                            bounces_count += 1
                    self.spoofing_cache = spoofing_cache
                    self.bounces_cache = bounces_cache
                    self.logger.info(f'Loaded {len(accounts)} accounts of which {spoofing_count} are allowed to spoof')
                    conn.close()

                    conn = get_session(self.dbconnection)
                    query = 'SELECT relay_account, domainname FROM relay_senderdomain'
                    result = conn.execute(text(query))
                    domain_cache = {}
                    domain_count = 0
                    senders = result.fetchall()
                    for line in senders:
                        key = line['relay_account']
                        value = line['domainname']
                        if key not in domain_cache:
                            domain_cache[key] = []
                        domain_cache[key].append(value)
                        domain_count += 1
                    self.domain_cache = domain_cache
                    self.logger.info(f'Loaded {len(domain_cache)} accounts and {domain_count} domains')
                    conn.close()

                    # success, no further attempts needed
                    attempts = 0
                except Exception as e:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    if attempts:
                        waitfor = random.random()
                        self.logger.warning(f'Exception while reloading (retry in {waitfor}s): {str(e)}')
                        time.sleep(waitfor)
                    else:
                        self.logger.error(f'Exception for {createPIDinfo()} while reloading: {str(e)}', exc_info=e)
            finally:
                self.lock.release()
    
    
    def can_spoof(self, relay_account):
        value = self.spoofing_cache.get(relay_account)
        self.logger.debug(f'sasl_user: {relay_account} spoofing: {value}')
        return value
    
    
    def can_bounce(self, relay_account):
        value = self.bounces_cache.get(relay_account)
        self.logger.debug(f'sasl_user: {relay_account} bounces: {value}')
        return value
    
    
    def can_send(self, relay_account, sender_domain):
        domains = self.domain_cache.get(relay_account, [])
        return sender_domain in domains


class SenderDomainRules(BMPRCPTMixin, BasicMilterPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section=section)

        self.logger = self._logger()
        
        self.requiredvars = {
            'testmode': {
                'default': 'False',
                'description': 'set to true to only log. set to false to actually reject policy violations'
            },
            'dbconnection': {
                'default': '',
                'description': 'SQLAlchemy Connection string'
            },
            'rejectmessage': {
                'default': '${from_domain} is not in my list of allowed sender domains for account ${sasl_user}',
                'description': 'reject message template for policy violators'
            },
            'reloadinterval': {
                'default': '300',
                'description': 'Interval until listings are refreshed'
            },
            'bounceblock': {
                'default': 'True',
                'description': 'Block bounces for selected sasl users'
            },
            'allow_rcpt': {
                'default': '',
                'description': 'list of recipients and recipient domains that are always allowed to receive mail',
            },
            'wltagname': {
                'default': 'skipmplugins',
                'description': 'tagname in case of WL hit (empty: don\'t set, skipmplugins to skip milter plugins)'
            },
            'wltagvalue': {
                'default': '',
                'description': 'tag content in case of WL hit (empty: don\'t set)'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }
        self._cache = None
    
    
    @property
    def cache(self):
        # create rules cache only when required
        if self._cache is None:
            self._cache = SenderDomainRulesCache(self.config.get(self.section, 'dbconnection'))
        return self._cache
    
    
    def lint(self, state=None) -> bool:
        from fuglu.funkyconsole import FunkyConsole
        if state and state not in self.state:
            # not active in current state
            return True

        fc = FunkyConsole()

        if not self.checkConfig():
            print(fc.strcolor("ERROR - config check", "red"))
            return False

        try:
            conn = get_session(self.config.get(self.section, 'dbconnection'))
            conn.execute('SELECT 1')
        except Exception as e:
            print(fc.strcolor('ERROR: ', "red"), f'DB Connection failed. Reason: {str(e)}')
            return False
        
        self.cache.dbconnection = self.config.get(self.section,'dbconnection')
        print(f'cached {len(self.cache.spoofing_cache)} spoofing entries '
              f'and {len(self.cache.domain_cache)} domain entries')
        return True
    
    
    def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        try:
            recipient = force_uString(recipient)
            if recipient is not None:
                to_address = strip_address(recipient)
                to_domain = extract_domain(to_address)
            else:
                to_address = None
                to_domain = None

            sender = force_uString(sess.sender)
            if sender is not None:
                from_address = strip_batv(strip_address(sender))
                from_address = decode_srs(from_address)
                from_domain = extract_domain(from_address)
            else:
                from_address = None
                from_domain = None

            sasl_user = force_uString(sess.sasl_user)

            # don't query locally generated messages
            if sasl_user is None or str(sasl_user).strip() == '':
                self.logger.debug(f'no sasl user -> continue')
                return sm.CONTINUE

            if from_domain is None or from_domain.strip() == '':
                #bounce
                if self.config.getboolean(self.section, 'bounceblock') and not self.cache.can_bounce(sasl_user):
                    return sm.REJECT, 'Bounce denied'
                else:
                    self.logger.debug(f'no from domain -> continue')
                    return sm.CONTINUE

            fields = sess.get_templ_dict()

            # always allow spoofing to certain recipients
            allow_rcpt = self.config.getlist(self.section, 'allow_rcpt')
            if to_domain in allow_rcpt or to_address in allow_rcpt:
                self.logger.info(f'{sess.id} sasl_user={sasl_user}, spoofing allowed to allowed mailbox {to_address}')
                # tag and continue (if possible)
                wltag = self.config.get(self.section, 'wltagvalue')
                wlname = self.config.get(self.section, 'wltagname')
                if wlname and wltag:
                    if wlname in sess.tags:
                        # append if already present
                        sess.tags[wlname] = f"{sess.tags[wlname]},{wltag}"
                    else:
                        # set tag
                        sess.tags[wlname] = wltag
                elif wlname:
                    self.logger.warning(f"allowed recipient: tag name defined but no value")
                elif wltag:
                    self.logger.error(f"allowed recipient: no tag name defined but value")
                else:
                    self.logger.info(f"allowed recipient: no tag no value defined -> accept mail")
                    return sm.ACCEPT

                return sm.CONTINUE

            self.cache.refreshtime = self.config.getint(self.section,'reloadinterval')
            self.cache.dbconnection = self.config.get(self.section,'dbconnection')
            
            
            #check if account is allowed to spoof any domain
            spoofing_allowed = self.cache.can_spoof(sasl_user)
            
            if spoofing_allowed is None:
                #no row found
                self.logger.warning(f'{sess.id} No relay config found for sasl_user={sasl_user}')
                return sm.TEMPFAIL, f'could not load configuration for user {sasl_user}'
            
            elif spoofing_allowed:
                self.logger.debug(f'{sess.id} sasl_user={sasl_user}, spoofing allowed, accepting sender domain')
                return sm.CONTINUE
            
            #check if senderdomain is in allowlist
            domain_found = self.cache.can_send(sasl_user, from_domain)  # returns True or False
            if domain_found:
                self.logger.debug(f'{sess.id} sasl_user={sasl_user} sender domain {from_domain} is in allow list.')
            else:
                self.logger.warning(f'{sess.id} Domain spoof: sasl_user={sasl_user} from={from_address} to={to_address}')
                testmode = self.config.getboolean(self.section, 'testmode')
                rejstring = self.config.get(self.section, 'rejectmessage')
                tmpl = Template(rejstring)
                rejectmessage = tmpl.safe_substitute(fields)
                if testmode:
                    self.logger.warning(f'{sess.id} Testmode (warn only): {rejectmessage}')
                else:
                    self.logger.debug(f'{sess.id} sasl_user={sasl_user}, reject with message: {rejectmessage}')
                    return sm.REJECT, rejectmessage

        except Exception as e:
            self.logger.error(f'Senderdomain plugin failed : {str(e)}')

        self.logger.debug(f'return continue')
        return sm.CONTINUE


class NoBounce(BMPRCPTMixin, BasicMilterPlugin):
    """
    do not send bounces to certain recipient domains (e.g. to prevent listing on backscatter rbls)
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        self.logger = self._logger()
        self.nobounce = None
        
        self.requiredvars = {
            'nobouncefile': {
                'default': '${confdir}/nobounce.txt',
                'description': 'list of domains to which bounces will be disallowed'
            },
            'rejectmessage': {
                'default': '${to_domain} does not accept bounces',
                'description': 'reject message template for policy violators'
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }
    
    
    def _init_lists(self):
        if self.nobounce is None:
            self.nobounce = FileList(self.config.get(self.section, 'nobouncefile'))
    
    
    def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) \
            -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        sender = force_uString(sess.sender)
        
        if sender is None or sender == '':
            self._init_lists()
            
            to_address = force_uString(recipient)
            to_address = strip_address(to_address)
            to_domain = extract_domain(to_address)
            
            nobounce = self.nobounce.get_list()
            if to_domain in nobounce:
                rejstring = self.config.get(self.section, 'rejectmessage')
                tmpl = Template(rejstring)
                
                fields = sess.get_templ_dict()
                
                rejectmessage = tmpl.safe_substitute(fields)
                return sm.REJECT, rejectmessage
        
        return sm.CONTINUE
    
    
    def lint(self, state=None) -> bool:
        from fuglu.funkyconsole import FunkyConsole
        
        if state and state not in self.state:
            # not active in current state
            return True
        
        fc = FunkyConsole()
        
        if not self.checkConfig():
            print(fc.strcolor("ERROR - config check", "red"))
            return False
        
        filepath = self.config.get(self.section, 'nobouncefile')
        if not os.path.exists(filepath):
            print(fc.strcolor('ERROR: ', "red"), f'nobouncefile {filepath} does not exist')
            return False
        
        self._init_lists()
        if self.nobounce is None:
            print('ERROR: failed to initialise no bounce list')
            print(fc.strcolor('ERROR: ', "red"), 'failed to initialise no bounce list')
            return False
        
        return True
    
    
class MilterData2Header(ScannerPlugin):
    """
    Save specific postfix environment data in a header.
    Currently only supports saving sasl login user name.
    Run this plugin in a milter mode fuglu to read data in e.g. a subsequently running after queue fuglu.
    Consider removing headers after reinjection into postfix.
    """
    
    def __init__(self,config,section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger=self._logger()
        self.requiredvars = {
            'headername_sasluser': {
                'default': 'X-SASL-Auth-User',
                'description': 'Name of header to store sasl login user name',
            },
        }


    def examine(self, suspect):
        hdr_sasl = self.config.get(self.section, 'headername_sasluser')
        suspect.add_header(hdr_sasl, suspect.sasl_login)
        return DUNNO



class TrapIntercept(ScannerPlugin):
    """
    This plugin intercepts mail to known trap recipients.
    A copy of the sent mail is bounced to a report address, mail is rejected and the sending account will be blocked.
    """
    def __init__(self,config,section=None):
        ScannerPlugin.__init__(self,config,section)
        self.logger=self._logger()
        
        self.requiredvars = {
            'traps_file': {
                'default': '${confdir}/traps.txt',
                'description': 'file with known traps'
            },
            
            'trap_regex': {
                'default': '',
                'description': 'regex to match traps by pattern'
            },
            
            'sender_exceptions_file': {
                'default': '${confdir}/trap_sender_exceptions.txt',
                'description': 'file with whitelisted senders'
            },
            
            'actioncode': {
                'default': 'REJECT',
                'description': "plugin action if policy is violated",
            },
            
            'rejectmessage': {
                'default': 'this account is sending spam - please contact your IT support',
                'description': 'reject/defer message template for policy violators'
            },
            
            'dbconnection': {
                'default': '',
                'description': 'sqlalchemy db connection string mysql://user:pass@host/database?charset=utf-8',
            },
            
            'sql_stmt_block': {
                'default': """
                    INSERT INTO relay_senderaccess (pattern, action, message, comment, relay_account, active)
                    VALUES (:sender, :action, :message, :comment, :relay_account, 1)
                    ON DUPLICATE KEY UPDATE edited=now(), active=1, comment=concat(comment, '\n', :comment);
                    """,
                'description': 'sql query to enable block'
            },
            
            'headername_sasluser': {
                'default': 'X-SASL-Auth-User',
                'description': 'Name of header to store sasl login user name',
            },
            
            'report_sender': {
                'default': '<>',
                'description': 'address of report generator. leave empty to use original mail sender, <> for empty envelope sender',
            },
            
            'report_recipient': {
                'default': '',
                'description': 'address of report recipient.',
            },
            
            'subject_template': {
                'default': 'Spam suspect from ${from_address}',
                'description': 'template of URI to sender account details',
            },
            
            'account_uri_template': {
                'default': '',
                'description': 'template of URI to sender account details',
            },
            
            'search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results',
            },
            
        }
        
        self.traps = None
        self.exceptions = None
        
        
    
    def _init_lists(self):
        if self.traps is None:
            traps_file = self.config.get(self.section, 'traps_file')
            if traps_file:
                self.traps = FileList(traps_file, additional_filters=email_normalise_ebl)
                
        if self.exceptions is None:
            sender_exceptions_file = self.config.get(self.section, 'sender_exceptions_file')
            if sender_exceptions_file:
                self.exceptions = FileList(sender_exceptions_file, additional_filters=email_normalise_ebl)
    
    
    
    def _static_traps(self, rcpt):
        is_trap = False
        rgx = self.config.get(self.section, 'trap_regex')
        if rgx and re.search(rgx, rcpt):
            is_trap = True
        return is_trap
    
    
    
    def examine(self, suspect):
        self._init_lists()
        exceptions = self.exceptions.get_list()
        if email_normalise_ebl(suspect.from_address) in exceptions or suspect.from_domain in exceptions:
            self.logger.debug('%s sender %s is on exception list' % (suspect.id, suspect.from_address))
            return DUNNO
        
        traps = set(self.traps.get_list())
        rcpt = email_normalise_ebl(suspect.to_address)
        if self._static_traps(rcpt) or rcpt in traps or suspect.to_domain in traps:
            if SQL_EXTENSION_ENABLED and suspect.from_address:
                self._block_sender(suspect)
            self._send_mail(suspect)
            actioncode = string_to_actioncode(self.config.get(self.section, 'actioncode'), self.config)
            message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {})
            return actioncode, message
        return DUNNO
    
    
    
    def lint(self):
        if not self.check_config():
            print('ERROR: config error')
            return False
        
        traps_file = self.config.get(self.section, 'traps_file')
        if not os.path.exists(traps_file):
            print('ERROR: cannot find traps_file %s' % traps_file)
            return False

        self._init_lists()
        if self.traps is None:
            print('ERROR: failed to initialise traps')
            return False
        if self.exceptions is None:
            print('ERROR: failed to initialise exceptions list')
            return False
        
        dbconnectstring = self.config.get(self.section, 'dbconnection')
        if not dbconnectstring:
            print('INFO: not using SQL backend')
            return True
        
        if not SQL_EXTENSION_ENABLED:
            print('WARNING: SQL extension not enabled, not using SQL database')
            return False
        
        try:
            dbsession = get_session(dbconnectstring)
            dbsession.execute('SELECT 1')
        except Exception as e:
            print('ERROR: failed to connect to SQL database: %s' % str(e))
            return False
        return True
    
    
    
    def _block_sender(self, suspect):
        dbconnectstring = self.config.get(self.section, 'dbconnection')
        dbsession = get_session(dbconnectstring)
        
        sql_stmt_block = self.config.get(self.section, 'sql_stmt_block')
        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        
        valdict = {
            'sender': suspect.from_address,
            'action': self.config.get(self.section, 'actioncode'),
            'message': self.config.get(self.section, 'rejectmessage'),
            'comment': '%s to %s' % (suspect.id, suspect.to_address),
            'relay_account': get_login_from_suspect(suspect, sasl_hdr),
        }
        
        try:
            dbsession.execute(sql_stmt_block, valdict)
        except Exception as e:
            self.logger.error('%s failed to block sender: %s' % (suspect.id, str(e)))
    
    
    
    def _send_mail(self, suspect):
        reportto = self.config.get(self.section, 'report_recipient')
        if not reportto:
            self.logger.info('%s not reported because report recipient is not defined' % suspect.id)
            return
        
        bounce = Bounce(self.config)
        reporter = self.config.get(self.section, 'report_sender') or suspect.from_address
        if reporter == '<>':
            reporter = ''
        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        login = get_login_from_suspect(suspect, sasl_hdr)
        tmpldata = {'sasl_login':login}
        account_uri = apply_template(self.config.get(self.section, 'account_uri_template'), suspect, tmpldata)
        search_uri  = apply_template(self.config.get(self.section, 'search_uri_template'), suspect, tmpldata)
        
        subject = suspect.get_message_rep().get('subject', '')
        subject = suspect.decode_msg_header(subject)
        
        # https://www.geeksforgeeks.org/send-mail-attachment-gmail-account-using-python/
        msg = MIMEMultipart()
        msg['From'] = reporter
        msg['To'] = reportto
        msg['Subject'] = apply_template(self.config.get(self.section, 'subject_template'), suspect, tmpldata)
        
        body  = 'Sender: %s\n' % suspect.from_address
        body += 'Trap Recipient: %s\n' % suspect.to_address
        body += 'Subject: %s\n' % subject
        if account_uri:
            body += f'Account: {account_uri}\n'
        if search_uri:
            body += f'Search: {search_uri}'
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        p = suspect.get_as_attachment('spam.eml')
        msg.attach(p)
        
        queueid = bounce.send(reporter, reportto, msg.as_bytes())
        self.logger.info("%s Spam Suspect mail sent to %s with queueid %s for sender %s and trap hit %s"
                         % (suspect.id, reporter, queueid, suspect.from_address, suspect.to_address))



class FuzorRateLimit(FuzorMixin, ScannerPlugin):
    """
    This plugin checks fuzor checksum of mail against redis database.
    if threshold is exceeded, a copy of the mail will be bounced to
    report address and all future mail is deferred until fuzor count
    is below threshold again.
    """
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        FuzorMixin.__init__(self)
        self.logger = self._logger()
        
        self.requiredvars.update({
            'threshold': {
                'default': '100',
                'description': 'alert threshold'
            },
            'sender_exception_file': {
                'description': 'file with senders that have a free pass to bulk'
            },
            'alert_exception_file': {
                'description': 'file with senders that do not trigger an alert when bulking (but still get rate limited)'
            },
            'demomode': {
                'default': 'False',
                'description': 'if set to True: do not block (defer), only alert'
            },
            'actioncode': {
                'default': 'DEFER',
                'description': "plugin action if if policy is violated",
            },
            'rejectmessage': {
                'default': 'rate limit exceeded',
                'description': 'reject/defer message template for policy violators'
            },
            'subject_ignore_keys': {
                'default': '',
                'description': 'comma separated list of keys in subject to ignore messages (case insensitive)'
            },
            'report_sender': {
                'default': '<>',
                'description': 'address of report generator. leave empty to use original mail sender, <> for empty envelope sender',
            },
            'report_recipient': {
                'default': '',
                'description': 'address of report recipient.',
            },
            'headername_sasluser': {
                'default': 'X-SASL-Auth-User',
                'description': 'Name of header to store sasl login user name',
            },
            'subject_template': {
                'default': 'Bulk suspect from ${from_address}',
                'description': 'template of URI to sender account details',
            },
            'account_uri_template': {
                'default': '',
                'description': 'template of URI to sender account details',
            },
            'search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results',
            },
        })
        
        self.sender_exceptions = None
        self.alert_exceptions = None
        try:
            self.subjectkeys = [k.lower().strip() for k in self.config.get(self.section, 'subject_ignore_keys').split(",")]
            # remove entries with empty strings
            self.subjectkeys = [k for k in self.subjectkeys if k]
        except Exception:
            self.subjectkeys = []
    
    
    def lint(self):
        if not self.check_config():
            print('ERROR: config error')
            return False
        
        sender_exception_file = self.config.get(self.section, 'sender_exception_file')
        if not os.path.exists(sender_exception_file):
            print('ERROR: cannot find sender_exception_file %s' % sender_exception_file)
            return False
        
        alert_exception_file = self.config.get(self.section, 'alert_exception_file')
        if not os.path.exists(alert_exception_file):
            print('ERROR: cannot find alert_exception_file %s' % alert_exception_file)
            return False
        
        self._init_lists()
        if self.sender_exceptions is None:
            print('ERROR: failed to initialise sender_exceptions')
            return False
        
        return True
    
    
    def _init_lists(self):
        if self.sender_exceptions is None:
            sender_exception_file = self.config.get(self.section, 'sender_exception_file')
            if sender_exception_file:
                self.sender_exceptions = FileList(sender_exception_file, additional_filters=email_normalise_ebl)
        
        if self.alert_exceptions is None:
            alert_exception_file = self.config.get(self.section, 'alert_exception_file')
            if alert_exception_file:
                self.alert_exceptions = FileList(alert_exception_file, additional_filters=email_normalise_ebl)
    
    
    def examine(self, suspect):
        if not REDIS_ENABLED:
            return DUNNO
        
        if suspect.from_address == '' or suspect.from_address is None:
            return DUNNO
        
        self._init_lists()
        if email_normalise_ebl(suspect.from_address) in set(self.sender_exceptions.get_list()):
            return DUNNO
        
        digest, count = suspect.get_tag('FuZor', (None, 0))
        
        if digest is None:
            self.logger.debug("digest is none... -> calculate")
            maxsize = self.config.getint(self.section, 'maxsize')
            if suspect.size > maxsize:
                stripoversize = self.config.getboolean(self.section, 'stripoversize')
                if stripoversize:
                    self.logger.debug('Fuzor: message too big (%u), stripping down to %u' % (suspect.size, maxsize))
                    msg = message_from_bytes(
                        suspect.source_stripped_attachments(maxsize=maxsize), _class=PatchedMessage
                    )
                else:
                    self.logger.debug('Fuzor: message too big (%u > %u), skipping' % (suspect.size, maxsize))
                    return DUNNO
            else:
                msg = suspect.get_message_rep()
            
            digest = FuzorDigest(msg).digest
            self.logger.debug("digest is %s" % digest if digest else "<none>")
            
            if digest is not None:
                suspect.debug('Fuzor digest = %s' % digest)
                try:
                    self._init_backend()
                except redis.exceptions.ConnectionError as e:
                    self.logger.error('failed to connect to redis server: %s' % str(e))
                    return DUNNO
                
                attempts = 2
                while attempts:
                    attempts -= 1
                    try:
                        count = self.backend.get(digest)
                        self.logger.debug("count is %u" % count)
                        attempts = 0
                    except redis.exceptions.TimeoutError as e:
                        msg = f'{suspect.id} failed getting count due to {str(e)}'
                        if attempts:
                            self.logger.warning(msg)
                        else:
                            self.logger.error(msg)
                            return DUNNO
                    except redis.exceptions.ConnectionError as e:
                        msg = f'{suspect.id} failed getting count due to {str(e)}, resetting connection'
                        if attempts:
                            self.logger.warning(msg)
                            self.backend = None
                            self._init_backend()
                        else:
                            self.logger.error(msg)
                            self.backend = None
                            return DUNNO
        
        threshold = self.config.getint(self.section, 'threshold')
        if count >= threshold:
            msgrep = suspect.get_message_rep()
            subject = msgrep.get("subject")
            if subject:
                subject = suspect.decode_msg_header(subject).lower()
            if msgrep.get('Auto-Submitted', '').lower().startswith('auto'):
                self.logger.info('%s skipped auto-submitted' % suspect.id)
            elif msgrep.get('X-Auto-Response-Suppress', '') != '':
                self.logger.info('%s no autoresponse requested, probably automated mail' % suspect.id)
            elif self.subjectkeys and any(key in subject for key in self.subjectkeys):
                self.logger.info('%s has ignore key(s) %s in subject'
                                 % (suspect.id, ",".join(k for k in self.subjectkeys if k in subject)))
            else:
                if not self.config.getboolean(self.section, 'demomode'):
                    # ------
                    # send mail if not already sent
                    # apply reject action
                    # ------
                    alert_exception_list = set(self.alert_exceptions.get_list())
                    if not email_normalise_ebl(suspect.from_address) in alert_exception_list and \
                            not suspect.from_domain in alert_exception_list:
                        self._check_and_send_mail(suspect, digest, count)
                    
                    actioncode = string_to_actioncode(self.config.get(self.section, 'actioncode'), self.config)
                    message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {})
                    self.logger.info("Sending %s for sender %s, id %s, hash %s (seen %u times)"
                                     % (actioncode_to_string(actioncode), suspect.from_address,
                                        suspect.id, digest, count))
                    return actioncode, message
                else:
                    # ---
                    # demo mode - only report
                    # ---
                    self.logger.info("Not blocking %s with hash %s (seen %u times) due to demo mode" % (suspect.id, digest, count))
        
        return DUNNO
    
    
    def _check_and_send_mail(self, suspect, digest, count):
        # check if mail has alredy been sent
        # using a simple counter here because I want to use the same backend (with same ttl) as
        # fuzor reportin (using the FuzorMixin)
        mailsent = 0
        digest_mailsent = None
        if digest:
            digest_mailsent = digest + "_mailsent"
            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    self._init_backend()
                    mailsent = self.backend.get(digest_mailsent)
                    attempts = 0
                except redis.exceptions.TimeoutError as e:
                    msg = f'{suspect.id} failed getting mail sent count due to {str(e)}'
                    self.logger.warning(msg) if attempts else self.logger.error(msg)
                except redis.exceptions.ConnectionError as e:
                    msg = f'{suspect.id} failed getting mail sent count due to {str(e)}, resetting connection'
                    self.logger.warning(msg) if attempts else self.logger.error(msg)
                    self.backend = None
        
        if mailsent == 0 and digest_mailsent is not None:
            self._send_mail(suspect, digest, count)
            # store in Redis mail has been sent...
            try:
                self._init_backend()
                mailsent = self.backend.increase(digest_mailsent)
                self.logger.info("mail for suspect %s hash %s has been sent %u" % (suspect.id, digest, mailsent))
            except redis.exceptions.TimeoutError as e:
                self.logger.error('%s failed increasing mail sent count due to %s' % (suspect.id, str(e)))
            except redis.exceptions.ConnectionError as e:
                self.logger.error('%s failed increasing mail sent count due to %s, resetting connection' % (suspect.id, str(e)))
                self.backend = None
    
    
    def _send_mail(self, suspect, digest, count):
        reportto = self.config.get(self.section, 'report_recipient')
        if not reportto:
            self.logger.info('%s not reported because report recipient is not defined' % suspect.id)
            return
        
        bounce = Bounce(self.config)
        reporter = self.config.get(self.section, 'report_sender') or suspect.from_address
        if reporter == '<>':
            reporter = ''
        
        sasl_hdr = self.config.get(self.section, 'headername_sasluser')
        login = get_login_from_suspect(suspect, sasl_hdr)
        tmpldata = {'sasl_login': login}
        account_uri = apply_template(self.config.get(self.section, 'account_uri_template'), suspect, tmpldata)
        search_uri = apply_template(self.config.get(self.section, 'search_uri_template'), suspect, tmpldata)
        
        subject = suspect.get_message_rep().get('subject', '')
        subject = suspect.decode_msg_header(subject)
        
        # https://www.geeksforgeeks.org/send-mail-attachment-gmail-account-using-python/
        msg = MIMEMultipart()
        msg['From'] = reporter
        msg['To'] = reportto
        msg['Subject'] = apply_template(self.config.get(self.section, 'subject_template'), suspect, tmpldata)
        
        body = 'Sender: %s\n' % suspect.from_address
        if account_uri:
            body += f'Account: {account_uri}\n'
        body += 'Fuzor hash: %s\n' % digest
        body += 'Fuzor count: %s\n' % count
        body += 'Subject: %s\n' % subject
        if search_uri:
            body += f'Search: {search_uri}'
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        p = suspect.get_as_attachment('bulk.eml')
        msg.attach(p)
        
        queueid = bounce.send(reporter, reportto, msg.as_bytes())
        self.logger.info("%s Bulk Suspect mail sent to %s with queueid %s for sender %s and Fuzor hash/count: %s/%u"
                         % (suspect.id, reportto, queueid, suspect.from_address, digest, count))



class PFQDRateLimit(BMPRCPTMixin, BasicMilterPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section=section)

        self.logger = self._logger()
        self.qstore = None

        self.requiredvars = {
            'maxqueue_domain': {
                'default': '15',
                'description': 'maximum queued mail for any given sender domain before deferring '
                               'further mail from this sender domain'
            },

            'maxqueue_user': {
                'default': '5',
                'description': 'maximum queued mail for any given sender before deferring further mail from this sender'
            },

            'active_queue_factor': {
                'default': '3',
                'description': 'by what multiplicator should active queue be weighted higher than deferred queue'
            },

            'redis_conn': {
                'default': '',
                'description': 'redis backend database connection: redis://host:port/dbid',
            },
            
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            
            'host_regex': {
                'default': '',
                'description': 'PFQD host filter regex'
            }
        }
    
    
    def _init_qstore(self):
        if self.qstore is None:
            class Args(object):
                pass
            args = Args()
            args.ttl=15
            args.hostname = get_outgoing_helo(self.config)
            args.redisconn = self.config.get(self.section, 'redis_conn')
            self.qstore = QStore(args=args)
    
    
    def _get_queue(self, from_domain, from_address, active_queue_factor):
        host_regex = self.config.get(self.section, 'host_regex')
        if host_regex:
            rgx = re.compile(host_regex)
        else:
            rgx = None
        relay_deferred = self.qstore.get_summary(QStore.QUEUE_DEFERRED, rgx)
        relay_active = self.qstore.get_summary(QStore.QUEUE_ACTIVE, rgx)
        deferred_size_dom = queue_size(relay_deferred, COL_FROM_DOM, from_domain)
        active_size_dom = queue_size(relay_active, COL_FROM_DOM, from_domain)
        deferred_size_user = queue_size(relay_deferred, COL_FROM_ADDR, from_address)
        active_size_user = queue_size(relay_active, COL_FROM_ADDR, from_address)
        qdom = deferred_size_dom + active_size_dom * active_queue_factor
        quser = deferred_size_user + active_size_user * active_queue_factor
        return qdom, quser
    
    
    def lint(self, state=None) -> bool:
        from fuglu.funkyconsole import FunkyConsole
        if state and state not in self.state:
            # not active in current state
            return True

        fc = FunkyConsole()

        if not self.checkConfig():
            print(fc.strcolor("ERROR - config check", "red"))
            return False

        if not REDIS_ENABLED:
            print(fc.strcolor("ERROR", "red"),' redis not available. this plugin will do nothing.' )
            return False

        try:
            self._init_qstore()
            redisconn = self.qstore._get_redis()
            redisconn.ping()

            from_address = 'info@schochvoegtli.ch'
            from_domain = extract_domain(from_address)
            active_queue_factor = self.config.getint(self.section, 'active_queue_factor')
            qdom, quser = self._get_queue(from_domain, from_address, active_queue_factor)
            print(f'Queue for {from_address}: {qdom}/{quser}')
        except Exception as e:
            self.logger.exception(e)
            print(fc.strcolor("ERROR", "red"), f' {str(e)}')
            return False

        return True
    
    
    def _is_welcomelisted(self, sess):
        tagname = 'welcomelisted'
        for key in list(sess.tags[tagname].keys()):
            val = sess.tags[tagname][key]
            if val:
                return True
        return False
    
    
    def examine_rcpt(self, sess: tp.Union[sm.MilterSession, asm.MilterSession], recipient: bytes) \
            -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        if not REDIS_ENABLED:
            return sm.CONTINUE

        from_address = sess.from_address
        if from_address:
            from_domain = sess.from_domain
        else:
            self.logger.info('no sender address found')
            return sm.CONTINUE

        if self._is_welcomelisted(sess):
            return sm.CONTINUE

        self._init_qstore()
        maxqueue_dom = self.config.getint(self.section, 'maxqueue_domain')
        maxqueue_user = self.config.getint(self.section, 'maxqueue_user')
        active_queue_factor = self.config.getint(self.section, 'active_queue_factor')
        
        queue_dom = queue_user = 0
        attempts = 2
        while attempts:
            attempts -= 1
            try:
                queue_dom, queue_user = self._get_queue(from_domain, from_address, active_queue_factor)
                attempts = 0
            except redis.ConnectionError as e:
                queue_dom = queue_user = 0
                msg = f"{sess.id} problem getting queue info: {str(e)}"
                if attempts:
                    self.logger.warning(msg)
                else:
                    self.logger.error(msg)

        if queue_dom > maxqueue_dom * active_queue_factor or queue_user > maxqueue_user * active_queue_factor:
            self.logger.info(f'current queue for {from_domain} is {queue_dom} and {from_address} is {queue_user}')
            return sm.TEMPFAIL, 'sender queue limit exceeded - try again later'

        return sm.CONTINUE