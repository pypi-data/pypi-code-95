# -*- coding: UTF-8 -*-
#   Copyright 2009-2021 Fumail Project
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
import os
import imaplib
import smtplib
import fnmatch
import time
import asyncio
import re
from domainmagic.mailaddr import split_mail
from fuglu.shared import ScannerPlugin, DUNNO, DELETE, SuspectFilter, AppenderPlugin, Suspect, get_outgoing_helo, apply_template, FileList
from fuglu.stringencode import force_uString
from fuglu.bounce import FugluSMTPClient, FugluAioSMTPClient, HAVE_AIOSMTP, SMTPException, Bounce
from urllib.parse import urlparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#TODO: reuse imap connections
#TODO: retries

class IMAPCopyPlugin(ScannerPlugin):
    """This plugins stores a copy of the message to an IMAP mailbox if it matches certain criteria (Suspect Filter).
The rulefile works similar to the archive plugin. As third column you have to provide imap account data in the form:

<protocol>://<username>:<password>@<servernameorip>[:port]/<mailbox>

<protocol> is one of:
 - imap (port 143, no encryption)
 - imap+tls (port 143 and StartTLS, only supported in Python 3)
 - imaps (port 993 and SSL)


"""
    def __init__(self,config,section=None):
        ScannerPlugin.__init__(self,config,section)
        
        self.requiredvars = {
            'imapcopyrules': {
                'default': '${confdir}/imapcopy.regex',
                'description': 'IMAP copy suspectFilter File',
            },
            
            'storeoriginal': {
                'default': 'True',
                'description': "if true/1/yes: store original message\nif false/0/no: store message probably altered by previous plugins, eg with spamassassin headers",
            },
            
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },
        }
        self.filter=None
        self.logger=self._logger()

        
    def examine(self, suspect: Suspect):
        try:
            action = self._run(suspect)
            message = None
        except Exception as e:
            self.logger.error('%s failed to copy to imap server due to %s' % (suspect.id, str(e)))
            action, message = self._problemcode()
        return action, message
    
    
    def process(self, suspect: Suspect, decision):
        try:
            action = self._run(suspect)
            if action == DELETE:
                self.logger.warning('%s imapcopy rule issued DELETE, ignoring in appender plugin' % suspect.id)
        except Exception as e:
            self.logger.error('%s failed to copy to imap server due to %s' % (suspect.id, str(e)))
        
        
    def _run(self, suspect: Suspect):
        imapcopyrules=self.config.get(self.section, 'imapcopyrules')
        if imapcopyrules is None or imapcopyrules=="":
            return DUNNO
        
        if not os.path.exists(imapcopyrules):
            self._logger().error('IMAP copy rules file does not exist : %s'%imapcopyrules)
            return DUNNO
        
        if self.filter is None:
            self.filter=SuspectFilter(imapcopyrules)
        
        (match,info)=self.filter.matches(suspect,extended=True)
        if match:
            delete = False
            field,matchedvalue,arg,regex=info
            if arg is not None and arg.lower()=='no':
                suspect.debug("Suspect matches imap copy exception rule")
                self.logger.info("""%s: Header %s matches imap copy exception rule '%s' """%(suspect.id,field,regex))
            else:
                if arg is None or (not arg.lower().startswith('imap') and arg.upper() != 'DELETE'):
                    self.logger.error("Unknown target format '%s' should be 'imap(s)://user:pass@host/folder'"%arg)
                    
                else:
                    self.logger.info("""%s: Header %s matches imap copy rule '%s' """%(suspect.id,field,regex))
                    if suspect.get_tag('debug'):
                        suspect.debug("Suspect matches imap copy rule (I would copy it if we weren't in debug mode)")
                    else:
                        if ' ' not in arg:
                            if arg.upper() != 'DELETE':
                                self.storeimap(suspect, arg)
                            else:
                                return DUNNO
                        else:
                            for value in arg.split():
                                if value.upper() == 'DELETE':
                                    self.logger.info("""%s: imap copy rule '%s' action DELETE""" % (suspect.id, regex))
                                    delete = True
                                    continue
                                self.storeimap(suspect, value)
                    if delete:
                        return DELETE
        else:
            suspect.debug("No imap copy rule/exception rule applies to this message")
        return DUNNO
    
    
    def imapconnect(self, imapurl: str, lintmode:bool=False):
        p=urlparse(imapurl)
        scheme=p.scheme.lower()
        host=p.hostname
        port=p.port
        username=p.username
        password=p.password
        folder=p.path[1:]
        
        if scheme == 'imaps':
            ssl = True
            tls = False
        elif scheme == 'imap+tls':
            ssl=False
            tls = True
        else:
            ssl = False
            tls = False
        
        
        if port is None:
            if ssl:
                port=imaplib.IMAP4_SSL_PORT
            else:
                port=imaplib.IMAP4_PORT
        try:
            if ssl:
                imap=imaplib.IMAP4_SSL(host=host,port=port)
            else:
                imap=imaplib.IMAP4(host=host,port=port)
        except Exception as e:
            ltype='IMAP'
            if ssl:
                ltype='IMAP-SSL'
            msg="%s Connection to server %s failed: %s" % (ltype, host, force_uString(e.args[0]))
            if lintmode:
                print(msg)
            else:
                self.logger.error(msg)
            return None
        
        if tls and hasattr(imap, 'starttls'):
            try:
                msg = imap.starttls()
                if msg[0] != 'OK':
                    if lintmode:
                        print(msg)
                    return None
                    
            except Exception as e:
                if lintmode:
                    print(str(e))
                return None
            
        try:
            imap.login(username, password)
        except Exception as e:
            msg="Login to server %s failed for user %s: %s" % (host, username, force_uString(e.args[0]))
            if lintmode:
                print(msg)
            else:
                self.logger.error(msg)
            return None
        
        try:
            mtype, count = imap.select(folder)
            excmsg = ''
        except Exception as e:
            excmsg = str(e)
            mtype = None
            
        if mtype=='NO' or excmsg:
            msg="Could not select folder %s@%s/%s : %s" % (username, host, folder, excmsg)
            if lintmode:
                print(msg)
            else:
                self.logger.error(msg)
            return None
        return imap
        
    
    def storeimap(self, suspect: Suspect, imapurl: str):
        imap=self.imapconnect(imapurl)
        if not imap:
            return
        #imap.debug=4
        p=urlparse(imapurl)
        folder=p.path[1:]
        
        if self.config.getboolean(self.section,'storeoriginal'):
            src=suspect.get_original_source()
        else:
            src=suspect.get_source()

        mtype, data = imap.append(folder,None,None,src)
        if mtype!='OK':
            self.logger.error('Could put store in IMAP. APPEND command failed: %s' % data)
        imap.logout()



    def lint(self):
        allok=(self.check_config() and self.lint_imap())
        return allok
    
    
    def lint_imap(self):
        #read file, check for all imap accounts
        imapcopyrules=self.config.get(self.section, 'imapcopyrules')
        if imapcopyrules!='' and not os.path.exists(imapcopyrules):
            print("Imap copy rules file does not exist : %s"%imapcopyrules)
            return False
        sfilter=SuspectFilter(imapcopyrules)

        accounts=[]
        for tup in sfilter.get_list():
            headername,pattern,arg = tup
            if arg not in accounts:
                if arg is None:
                    print("Rule %s %s has no imap copy target" % (headername, pattern.pattern))
                    return False
                if arg.lower()=='no':
                    continue
                elif arg.lower() == 'delete':
                    return False
                if ' ' not in arg:
                    accounts.append(arg)
                else:
                    for value in arg.split():
                        if value == 'DELETE': continue
                        accounts.append(value)
        
        success = True
        for acc in accounts:
            msg = 'OK'
            p=urlparse(acc)
            host=p.hostname
            username=p.username
            folder=p.path[1:]
            try:
                imap=self.imapconnect(acc,lintmode=True)
                if not imap:
                    msg = 'ERROR: Failed to connect'
                    success = False
                else:
                    imap.close()
            except Exception as e:
                msg = 'ERROR: %s' % str(e)
            print("Checked %s@%s/%s : %s" % (username, host, folder, msg))
        if not success:
            return False

        return True


class FeedList(FileList):
    def __init__(self, *args, **kwargs):
        self.target_servers = []
        self.target_domains = {}
        self.target_globs = {}
        FileList.__init__(self, *args, **kwargs)
    
    
    def _parse_server_args(self, fields):
        target_str = fields[0]
        target_str = target_str.strip(';')
        host = target_str
        args = {}
        
        if ';' in target_str:
            values = target_str.split(';')
            host = values[0]
            for val in values[1:]:
                k,v = val.split('=', 1)
                k = k.lower()
                if k in ['port', 'timeout']:
                    v = int(v)
                elif k in ['tls', 'xclient']:
                    v = v.lower() in ['yes', 'true', '1', 'on']
                args[k] = v
                
        if fields[1] == '*':
            exceptions = []
            for item in fields[2:]:
                if item.startswith('!'):
                    exceptions.append(item[1:].lower())
            if exceptions:
                args['exc'] = exceptions
        return host.lower(), args
    
    
    def _parse_lines(self, lines):
        target_servers = []
        target_domains = {}
        target_globs = {}
    
        for line in lines:
            line = self._apply_linefilters(line)
            if not line:
                continue
        
            fields = line.split()
            if len(fields)==1:
                self.logger.error('not a valid feed defintion: %s' % line)
                continue
            
            try:
                server_name, server_args = self._parse_server_args(fields)
            except Exception:
                self.logger.error('not a valid server defintion: %s' % fields[0])
                continue
            
            server = (server_name, server_args)
            if fields[1] == '*':
                if server not in target_servers:
                    target_servers.append(server)
            else:
                domains = fields[1:]
                for domain in domains:
                    domain = domain.lower()
                    if domain.startswith('!'):
                        # excludes are not supported in non-wildcard definitions
                        continue
                    elif domain.startswith('*.'):
                        try:
                            if server not in target_globs[domain]:
                                target_globs[domain].append(server)
                        except KeyError:
                            target_globs[domain] = [server]
                    else:
                        try:
                            if server not in target_domains[domain]:
                                target_domains[domain].append(server)
                        except KeyError:
                            target_domains[domain] = [server]
        
        self.target_servers = target_servers
        self.target_domains = target_domains
        self.target_globs = target_globs
        return []
        
    
    def get_targets(self):
        """Returns the current list. If the file has been changed since the last call, it will rebuild the list automatically."""
        if self.filename is not None:
            self._reload_if_necessary()
        return self.target_servers, self.target_domains, self.target_globs


class MailFeed(AppenderPlugin):
    """Send a copy of a message to a certain target server"""
    def __init__(self, config, section=None):
        AppenderPlugin.__init__(self, config, section)
        self.logger = self._logger()
        
        self.requiredvars = {
            'targetfile': {
                'default': '${confdir}/mailfeeds.txt',
                'description': """file with feed targets.
                format: target.server[;opt=val;opt=val] domain1 domain2 or * for all domains
                possible options: port=587;tls=True;xclient=True;user=user;pass=pass;from=<>;to=*;timeout=30
                options tls, xclient, and from will override the global defaults defined in plugin config""",
            },
            
            'mail_types': {
                'default': 'any',
                'description': 'comma separated list of mail classes to be delivered: any, ham, spam, virus, blocked'
            },
    
            'from_address': {
                'default': '<>',
                'description': 'envelope sender to be used. set to <> for empty envelope sender, set to * to use original sender',
            },
            
            'to_address': {
                'default': '${to_localpart}@${target}',
                'description': 'template for envelope recipient to be used. set to * to use original recipient. will always be set to @target if domain is equals to fuglu hostname',
            },
            
            'use_tls': {
                'default': 'True',
                'description:': 'always use StartTLS when sending mail'
            },
            
            'use_xclient': {
                'default': 'False',
                'description:': 'send original client information via XCLIENT command'
            },
            
            'original_sender_header': {
                'default': 'X-Original-Sender',
                'description': 'add original sender in this header'
            },
            
            'original_recipient_header': {
                'default': 'X-Original-Recipient',
                'description': 'add original sender in this header'
            },
            
        }
        
        self.mailfeeds = None
        self.event_loop = None
    
    
    def _load_mailfeeds(self):
        if self.mailfeeds is None:
            targetfile = self.config.get(self.section, 'targetfile')
            self.mailfeeds = FeedList(targetfile)
    
    
    def _get_xclient_args(self, suspect: Suspect):
        args = {}
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            clienthelo, clientip, clienthostname = clientinfo
            args['HELO'] = clienthelo
            args['ADDR'] = clientip
            args['NAME'] = clienthostname
        return args
    
    
    def _log_response(self, prefix, response, level='debug'):
        if len(response) == 2:
            logmessage = f'{prefix} got response {response[0]} {force_uString(response[1])}'
        else:
            logmessage = f'{prefix} got response {response}'
        if 200 <= int(response[0]) <= 299:
            logger = getattr(self.logger, level)
            logger(logmessage)
        else:
            self.logger.error(logmessage)
    
    
    def _get_content(self, suspect: Suspect) -> bytes:
        msg_buffer = suspect.get_original_source()
        # prepend header with original sender
        original_sender_header = self.config.get(self.section, 'original_sender_header')
        if original_sender_header:
            msg_buffer = Suspect.prepend_header_to_source(original_sender_header, suspect.from_address, msg_buffer)
        # prepend header with original recipient
        original_recipient_header = self.config.get(self.section, 'original_recipient_header')
        if original_recipient_header:
            msg_buffer = Suspect.prepend_header_to_source(original_recipient_header, suspect.from_address, msg_buffer)
        return msg_buffer
    
    
    def _send_sync(self, suspect: Suspect, target_host: str, target_args: dict, from_address: str, to_address: str, retry: int = 3):
        try:
            port = target_args.get('port', smtplib.SMTP_PORT)
            timeout = target_args.get('timeout', 60)
            helostring = get_outgoing_helo(self.config)
            smtp_server = FugluSMTPClient(target_host, port=port, timeout=timeout, local_hostname=helostring)
            use_tls = target_args.get('tls', self.config.getboolean(self.section, 'use_tls'))
            use_xclient = target_args.get('xclient', self.config.getboolean(self.section, 'use_xclient'))
            use_auth = target_args.get('user') and target_args.get('pass')
            if use_tls:
                try:
                    starttls_resp = smtp_server.starttls()
                    self._log_response('%s sent starttls to %s' % (suspect.id, target_host), starttls_resp)
                except smtplib.SMTPNotSupportedError as e:
                    self.logger.error('%s failed to start tls to target server %s due to: %s' % (suspect.id, target_host, str(e)))
            if use_xclient:
                xclient_args = self._get_xclient_args(suspect)
                try:
                    if xclient_args:
                        xclient_resp = smtp_server.xclient(xclient_args)
                        self._log_response('%s sent xclient args %s to %s' % (suspect.id, xclient_args, target_host), xclient_resp)
                except smtplib.SMTPNotSupportedError as e:
                    self.logger.error('%s xclient failed with target server %s due to: %s' % (suspect.id, target_host, str(e)))
            if use_auth:
                try:
                    login_resp = smtp_server.login(target_args.get('user'), target_args.get('pass'))
                    self._log_response('%s sent authentication for user %s to %s' % (suspect.id, target_args.get('user'), target_host), login_resp)
                except smtplib.SMTPNotSupportedError as e:
                    self.logger.error('%s failed to authenticate at target server %s with user %s due to: %s' % (suspect.id, target_host, target_args.get('user'), str(e)))
            content = self._get_content(suspect)
            fails = smtp_server.sendmail(force_uString(from_address), force_uString(to_address), content)
            sendmail_resp = (smtp_server.lastservercode, smtp_server.lastserveranswer)
            self._log_response('%s sent message for %s to %s' % (suspect.id, to_address, target_host), sendmail_resp, level='info')
            try:
                quit_resp = smtp_server.quit()
                self._log_response('%s sent quit to %s' % (suspect.id, target_host), quit_resp)
            except Exception as e:
                self.logger.debug('%s error sending quit to %s: %s' % (suspect.id, target_host, str(e)))
        except Exception as e:
            self.logger.error('%s failed to forward to %s due to %s' % (suspect.id, target_host, str(e)))
            if retry > 0:
                time.sleep((4-retry)/2)
                fails = self._send_sync(suspect, target_host, target_args, from_address, to_address, retry=retry-1)
            else:
                fails = {to_address: str(e)}
        return fails
    
    
    async def _send_async(self, suspect: Suspect, target_host: str, target_args: dict, from_address: str, to_address: str, retry: int = 3):
        try:
            port = target_args.get('port', smtplib.SMTP_PORT)
            timeout = target_args.get('timeout', 60)
            helostring = get_outgoing_helo(self.config)
            use_tls = target_args.get('tls', self.config.getboolean(self.section, 'use_tls'))
            smtp_server = FugluAioSMTPClient(hostname=target_host, port=port, source_address=helostring, start_tls=use_tls, timeout=timeout)
            conn_resp = await smtp_server.connect()
            self._log_response('%s connected to %s' % (suspect.id, target_host), conn_resp)
            use_xclient = target_args.get('xclient', self.config.getboolean(self.section, 'use_xclient'))
            use_auth = target_args.get('user') and target_args.get('pass')
            if use_xclient:
                xclient_args = self._get_xclient_args(suspect)
                try:
                    if xclient_args:
                        xclient_resp = await smtp_server.xclient(xclient_args)
                        self._log_response('%s sent xclient args %s to %s' % (suspect.id, xclient_args, target_host), xclient_resp)
                except SMTPException as e:
                    self.logger.error('%s xclient failed with target server %s due to: %s' % (suspect.id, target_host, str(e)))
            if use_auth:
                try:
                    login_resp = await smtp_server.login(target_args.get('user'), target_args.get('pass'))
                    self._log_response('%s sent authentication for user %s to %s' % (suspect.id, target_args.get('user'), target_host), login_resp)
                except SMTPException as e:
                    self.logger.error('%s failed to authenticate at target server %s with user %s due to: %s' % (suspect.id, target_host, target_args.get('user'), str(e)))
            content = self._get_content(suspect)
            fails, logmsg = await smtp_server.sendmail(from_address, to_address, content)
            self._log_response('%s sent message for %s to %s' % (suspect.id, to_address, target_host), logmsg, level='info')
            try:
                quit_resp = await smtp_server.quit()
                self._log_response('%s sent quit to %s' % (suspect.id, target_host), quit_resp)
            except Exception as e:
                self.logger.debug('%s error sending quit to %s: %s' % (suspect.id, target_host, str(e)))
        except Exception as e:
            import traceback
            self.logger.error('%s failed to forward to %s due to %s' % (suspect.id, target_host, str(e)))
            self.logger.error(traceback.format_exc())
            if retry > 0:
                time.sleep((4-retry)/2)
                fails = await self._send_async(suspect, target_host, target_args, from_address, to_address, retry=retry-1)
            else:
                fails = {to_address: str(e)}
        return fails
    
    
    def _send_mail(self, target_host: str, target_args: dict, suspect: Suspect, retry: int = 3):
        exceptions = target_args.get('exc', [])
        if suspect.to_domain in exceptions:
            self.logger.debug(f'{suspect.id} skipping sending to {target_host}')
            return
        
        self.logger.debug(f'{suspect.id} to {target_host} with args {target_args}')
        
        from_address = target_args.get('from', self.config.get(self.section, 'from_address'))
        if from_address == '<>':
            from_address = ''
        elif from_address == '*':
            from_address = suspect.from_address
        
        to_template = target_args.get('to', self.config.get(self.section, 'to_address'))
        if to_template == '*':
            to_address = suspect.to_address
        else:
            to_address = apply_template(to_template, suspect, {'target':target_host})
        to_user, to_domain = split_mail(to_address)
        if to_domain == get_outgoing_helo(self.config):
            to_address = f'{to_user}@{target_host}'
        
        disable_aiosmtp = self.config.getboolean('performance', 'disable_aiosmtp')
        if HAVE_AIOSMTP and not disable_aiosmtp:
            if self.event_loop is None:
                try:
                    self.event_loop = asyncio.get_running_loop()
                except AttributeError:
                    # python 3.6
                    self.event_loop = asyncio.get_event_loop()
            fails = self.event_loop.run_until_complete(self._send_async(suspect, target_host, target_args, from_address, to_address, retry=retry-1))
        else:
            fails = self._send_sync(suspect, target_host, target_args, from_address, to_address)
        
        if not fails:
            self.logger.debug(f'{suspect.id} for {to_address} forwarded to {target_host}')
        else:
            self.logger.error(f'{suspect.id} delivery failures to {target_host} for {fails}')
    
    
    def lint(self):
        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()

        if not self.check_config():
            print(fc.strcolor("ERROR: ", "red"), "config check")
            return False
        
        if HAVE_AIOSMTP:
            print(fc.strcolor("INFO: ", "blue"), 'aiosmtplib available')

        targetfile = self.config.get(self.section, 'targetfile')
        if not os.path.exists(targetfile):
            print(fc.strcolor("ERROR: ", "red"), 'target file %s not found' % targetfile)
            return False
        
        self._load_mailfeeds()
        target_servers, target_domains, target_globs = self.mailfeeds.get_targets()
        print(fc.strcolor("INFO: ", "blue"), f'global feed to servers: {", ".join([s[0] for s in target_servers])}')
        print(fc.strcolor("INFO: ", "blue"), f'forwarding {len(target_domains)} domains')
        print(fc.strcolor("INFO: ", "blue"), f'forwarding {len(target_globs)} glob rules')
        
        return True
    
    
    def _feed(self, suspect: Suspect):
        targets_sent = []
        to_domain = suspect.to_domain.lower()
        
        mail_types = self.config.getlist(self.section, 'mail_types', lower=True)
        do_send = 'any' in mail_types \
            or 'ham' in mail_types and suspect.is_ham() \
            or 'spam' in mail_types and suspect.is_spam() \
            or 'virus' in mail_types and suspect.is_virus() \
            or 'blocked' in mail_types and suspect.is_blocked()
        
        if not do_send:
            self.logger.debug(f'{suspect.id} not sending as msg is not in types {", ".join(mail_types)}')
            return
        
        self._load_mailfeeds()
        target_servers, target_domains, target_globs = self.mailfeeds.get_targets()
        
        for target_server in target_servers:
            self._send_mail(target_server[0], target_server[1], suspect)
            targets_sent.append(target_server)
        for target_server in target_domains.get(to_domain, []):
            if target_server not in targets_sent:
                self._send_mail(target_server[0], target_server[1], suspect)
                targets_sent.append(target_server)
        for target_glob in target_globs.keys():
            if fnmatch.fnmatch(to_domain, target_glob):
                for target_server in target_globs[target_glob]:
                    if target_server not in targets_sent:
                        self._send_mail(target_server[0], target_server[1], suspect)
                        targets_sent.append(target_server)
    
    
    def examine(self, suspect: Suspect):
        self._feed(suspect)
        return DUNNO
    
    
    def process(self, suspect: Suspect, decision):
        self._feed(suspect)



class AutoReport(AppenderPlugin):
    def __init__(self, config, section=None):
        AppenderPlugin.__init__(self, config, section)
        self.logger = self._logger()
        
        self.requiredvars = {
            'trap_regex': {
                'default': '',
                'description': 'regex to match traps by pattern'
            },
            
            'report_sender': {
                'default': '<>',
                'description': 'address of report generator. leave empty to use original mail sender, <> for empty envelope sender',
            },
            
            'report_recipient': {
                'default': '',
                'description': 'address of report recipient',
            },
            
            'bounce_recipient': {
                'default': '',
                'description': 'address of bounce recipient',
            },
            
            'subject_template': {
                'default': 'Spam suspect from ${from_address}',
                'description': 'template of URI to sender account details',
            },
            
            'original_sender_header': {
                'default': 'X-Original-Sender',
                'description': 'add original sender in this header'
            },
            
            'message_uri_template': {
                'default': '',
                'description': 'template of URI to log showing message details',
            },
            
            'sender_search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results by sender',
            },
            
            'server_search_uri_template': {
                'default': '',
                'description': 'template of URI to log search results by sending server',
            },
        }
    
    
    def process(self, suspect, decision):
        to_address = suspect.to_address
        if not self._static_traps(to_address):
            return DUNNO
        
        if suspect.is_ham():
            self._send_mail(suspect)
        self._hash_mail(suspect)
        return DUNNO
    
    
    
    def _static_traps(self, rcpt):
        is_trap = False
        rgx = self.config.get(self.section, 'trap_regex')
        if rgx and re.search(rgx, rcpt):
            is_trap = True
        return is_trap
    
    
    def _send_mail(self, suspect):
        reportto = self.config.get(self.section, 'report_recipient')
        if not reportto:
            self.logger.info('%s not reported because report recipient is not defined' % suspect.id)
            return
    
        bounce = Bounce(self.config)
        reporter = self.config.get(self.section, 'report_sender') or suspect.from_address
        if reporter == '<>':
            reporter = ''
        
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            clienthelo, clientip, clienthostname = clientinfo
        else:
            clienthelo = clientip = clienthostname = None
        
        subject = suspect.get_message_rep().get('subject', '')
        subject = suspect.decode_msg_header(subject)

        message_uri = apply_template(self.config.get(self.section, 'message_uri_template'), suspect)
        sender_search_uri = apply_template(self.config.get(self.section, 'sender_search_uri_template'), suspect)
        server_search_uri = apply_template(self.config.get(self.section, 'server_search_uri_template'), suspect)
        
        # https://www.geeksforgeeks.org/send-mail-attachment-gmail-account-using-python/
        # msg = MIMEMultipart()
        msg = MIMEMultipart()
        msg['From'] = reporter
        msg['To'] = reportto
        msg['Subject'] = apply_template(self.config.get(self.section, 'subject_template'), suspect)
        
        body = 'Sender: %s\n' % suspect.from_address
        body += 'Trap Recipient: %s\n' % suspect.to_address
        body += 'Subject: %s\n' % subject
        body += 'Spam: %s\n' % suspect.is_spam()
        body += 'Server info: %s / %s / %s\n' % (clientip, clienthostname, clienthelo)
        if message_uri:
            body += f'Message: {message_uri}'
        if sender_search_uri:
            body += f'From: {sender_search_uri}'
        if server_search_uri:
            body += f'Server: {server_search_uri}'
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        p = suspect.get_as_attachment('spam.eml')
        msg.attach(p)
        
        queueid = bounce.send(reporter, reportto, msg.as_bytes())
        self.logger.info("%s Spam report sent to %s with queueid %s for sender %s and trap hit %s" % (suspect.id, reporter, queueid, suspect.from_address, suspect.to_address))
    
    
    def _hash_mail(self, suspect):
        reportto = self.config.get(self.section, 'bounce_recipient')
        if not reportto:
            self.logger.info('%s not reported because bounce recipient is not defined' % suspect.id)
            return
        
        bounce = Bounce(self.config)
        reporter = '<>'
        
        # use buffer directly to prevent python EmailMessage conversion errors
        msg_buffer = suspect.get_original_source()
        # prepend header with original sender
        original_sender_header = self.config.get(self.section, 'original_sender_header')
        if original_sender_header:
            msg_buffer = Suspect.prepend_header_to_source(original_sender_header, suspect.from_address, msg_buffer)
        
        queueid = bounce.send(reporter, reportto, msg_buffer)
        self.logger.info("%s Spam hashed with queueid %s " % (suspect.id, queueid))