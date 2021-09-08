# -*- coding: UTF-8 -*-
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

import smtplib
import logging
import os
import email
import socket
import re
import ssl
import asyncio
from email.utils import formatdate, make_msgid
from email.header import Header
from .shared import apply_template, FileList, extract_domain, get_outgoing_helo, deprecated
from .stringencode import force_bString, force_uString

try:
    from aiosmtplib import SMTP as aioSMTP
    from aiosmtplib.errors import SMTPException
    HAVE_AIOSMTP = True
except ImportError:
    class aioSMTP(object):
        pass
    class SMTPException(Exception):
        pass
    HAVE_AIOSMTP = False


requeue_rgx = re.compile("""2.0.0 Ok: queued as (?P<requeueid>[A-Za-z0-9]{12,18}|[A-Z0-9]{10,12})""")
def queueid_from_postfixreply(logline):
    queueid = None
    m = requeue_rgx.search(logline)
    if m is not None:
        queueid = m.groupdict()['requeueid']
    return queueid


class FugluSMTPClient(smtplib.SMTP):
    """
    This class patches SMTPLib
    improvements:
    - get response code message from postfix when using sendmail() (stored in different vars)
    - support xclient
    """
    queueid = None
    lastserveranswer = None
    lastservercode = None
        
    
    # usually no need to call this manually (may block infinitely)
    def getreply(self):
        code, response = smtplib.SMTP.getreply(self)
        self.lastserveranswer = response
        self.lastservercode = code
        queueid = queueid_from_postfixreply(response.decode())
        if queueid is not None:
            self.queueid = queueid
        return code, response
    
    
    def xclient(self, xclient_args=None):
        self.ehlo_or_helo_if_needed()
        if not 'xclient' in self.esmtp_features:
            raise smtplib.SMTPNotSupportedError("SMTP XCLIENT extension not supported by server.")
        
        if xclient_args:
            xclient_cmds = self.esmtp_features['xclient'].split()
            if 'ADDR' in xclient_args and ':' in xclient_args['ADDR'] and not xclient_args['ADDR'].startswith('IPV6:'):
                xclient_args['ADDR'] = 'IPV6:%s' % xclient_args['ADDR']
            values = [f'{k.upper()}={force_uString(v)}' for k,v in xclient_args.items() if v and k.upper() in xclient_cmds]
            xclient_str = ' '.join(values)
            if xclient_str:
                return self.docmd('XCLIENT', xclient_str)


class FugluAioSMTPClient(aioSMTP):
    """
    This class patches aioSMTPLib
    improvements:
    - do not check certificates during starttls
    - support xclient
    """
    async def starttls(self, *args, **kwargs):
        if not kwargs.get('tls_context'):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            kwargs['tls_context'] = ctx
        return await aioSMTP.starttls(self, *args, **kwargs)
    
    
    async def xclient(self, xclient_args=None):
        await self._ehlo_or_helo_if_needed()
        if not self.supports_extension('xclient'):
            raise SMTPException("SMTP XCLIENT extension not supported by server.")

        if xclient_args:
            xclient_cmds = self.esmtp_extensions['xclient']
            if 'ADDR' in xclient_args and ':' in xclient_args['ADDR'] and not xclient_args['ADDR'].startswith('IPV6:'):
                xclient_args['ADDR'] = 'IPV6:%s' % xclient_args['ADDR']
            values = [f'{k.upper()}={force_uString(v)}' for k, v in xclient_args.items() if v and k.upper() in xclient_cmds]
            xclient_str = ' '.join(values)
            if xclient_str:
                response = await self.execute_command(b'XCLIENT', force_bString(xclient_str))
                return response


class Bounce(object):

    """Send Mail (Bounces)"""

    def __init__(self, config):
        self.logger = logging.getLogger('fuglu.bouncer')
        self.config = config
        self.nobounce = None
        self.event_loop = None
    
    
    def _init_nobounce(self):
        if self.nobounce is None:
            try:
                filepath = self.config.get('main', 'nobouncefile')
            except Exception:
                filepath = None
            if filepath and os.path.exists(filepath):
                self.nobounce = FileList(filepath)
            elif filepath:
                self.logger.warning('nobouncefile %s not found' % filepath)
    
    
    def _add_required_headers(self, recipient, messagecontent):
        """add headers required for sending automated mail"""

        msgrep = email.message_from_bytes(force_bString(messagecontent))
        msgrep.set_charset("utf-8") # define unicode because the messagecontent is unicode

        if not 'to' in msgrep:
            msgrep['To'] = Header("<%s>" % recipient).encode()

        if not 'From' in msgrep:
            msgrep['from'] = Header("<MAILER-DAEMON@%s>" % socket.gethostname()).encode()

        if not 'auto-submitted' in msgrep:
            msgrep['auto-submitted'] = Header('auto-generated').encode()

        if not 'date' in msgrep:
            msgrep['Date'] = formatdate(localtime=True)

        if not 'Message-id' in msgrep:
            msgrep['Message-ID'] = make_msgid()

        return msgrep.as_string()
    
    
    def send_template_file(self, recipient, templatefile, suspect, values):
        """Send a E-Mail Bounce Message

        Args:
            recipient    (str):  Message recipient (bla@bla.com)
            templatefile (str): Template to use
            suspect      (fuglu.shared.Suspect) suspect that caused the bounce
            values            :Values to apply to the template. ensure all values are of type <str>

        If the suspect has the 'nobounce' tag set, the message will not be sent. The same happens
        if the global configuration 'disablebounces' is set.
        """

        if not os.path.exists(templatefile):
            self.logger.error('Template file does not exist: %s' % templatefile)
            return

        with open(templatefile) as fp:
            filecontent = fp.read()

        queueid = self.send_template_string(recipient, filecontent, suspect, values)
        return queueid
    
    
    def send_template_string(self, recipient, templatecontent, suspect, values):
        """Send a E-Mail Bounce Message

        If the suspect has the 'nobounce' tag set, the message will not be sent. The same happens
        if the global configuration 'disablebounces' is set.

        Args:
            recipient       (unicode or str) : Message recipient (bla@bla.com)
            templatecontent (unicode or str) : Template to use
            suspect         (fuglu.shared.Suspect) : suspect that caused the bounce
            values       : Values to apply to the template
        """
        if suspect.get_tag('nobounce'):
            self.logger.info('Not sending bounce to %s - bounces disabled by plugin' % recipient)
            return

        message = apply_template(templatecontent, suspect, values)
        try:
            message = self._add_required_headers(recipient, message)
        except Exception as e:
            self.logger.warning('Bounce message template could not be verified: %s' % str(e))

        self.logger.debug('Sending bounce message to %s' % recipient)
        fromaddress = "<>"
        queueid = self.send(fromaddress, recipient, message)
        return queueid

    def _get_targethost(self):
        targethost: str = self.config.get('main', 'outgoinghost')
        if targethost == '${injecthost}':
            # fall back to bindaddress
            targethost = self.config.get('main', 'bindaddress')
            if targethost == "0.0.0.0":
                raise ValueError(f"Bouncer: targethost can't be set to '${{injecthost}}' "
                                 f"if bindaddress is set to '0.0.0.0'")
        elif targethost.startswith("$"):
            # extract target host from environment variable
            env_targethost = os.environ[targethost[1:]]
            if not env_targethost:
                raise ValueError(f"Bouncer: Could not extract outgoing host from environment var '{targethost}'")
            targethost = env_targethost
        if not targethost or (isinstance(targethost, str) and not targethost.strip()):
            raise ValueError("Bouncer: No targethost defined for Bouncer, please define valid outgoinghost in config!")
        return targethost
    
    
    def _send_sync(self, fromaddress, toaddress, message):
        """really send message"""
        targethost = self._get_targethost()
        outgoingport = self.config.getint('main', 'outgoingport')
        helostring = get_outgoing_helo(self.config)
        smtp_server = FugluSMTPClient(host=targethost, port=outgoingport, local_hostname=helostring)
        smtp_server.sendmail(fromaddress, toaddress, message)
        smtp_server.quit()
        return smtp_server.queueid
    
    
    def _send_async(self, fromaddress, toaddress, message):
        targethost = self._get_targethost()
        outgoingport = self.config.getint('main', 'outgoingport')
        helostring = get_outgoing_helo(self.config)
        smtp_server = FugluAioSMTPClient(hostname=targethost, port=outgoingport, source_address=helostring)
        smtp_server.connect()
        send_resp = smtp_server.sendmail(fromaddress, toaddress, message)
        smtp_server.quit()
        return smtp_server.parse_postfixreply(send_resp[1])
    
    
    def send(self, fromaddress, toaddress, message):
        if self.config.getboolean('main', 'disablebounces'):
            self.logger.info('Bounces are disabled in config - not sending message to %s' % toaddress)
            return
        
        self._init_nobounce()
        if self.nobounce and extract_domain(toaddress) in self.nobounce.get_list():
            self.logger.info('Bounces to this rcpt are disabled - not sending message to %s' % toaddress)
            return
        
        disable_aiosmtp = self.config.getboolean('performance', 'disable_aiosmtp')
        if HAVE_AIOSMTP and not disable_aiosmtp:
            if self.event_loop is None:
                try:
                    self.event_loop = asyncio.get_running_loop()
                except AttributeError:
                    # python 3.6
                    self.event_loop = asyncio.get_event_loop()
            queueid = self.event_loop.run_until_complete(self._send_async(fromaddress, toaddress, message))
        else:
            queueid = self._send_sync(fromaddress, toaddress, message)
        return queueid
    
    
    @deprecated
    def _send(self, fromaddress, toaddress, message):
        """deprecated version of send()"""
        self.send(fromaddress, toaddress, message)
    
    
    def lint(self):
        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()

        try:
            targethost = self._get_targethost()
            outgoingport = self.config.getint('main', 'outgoingport')
            helostring = get_outgoing_helo(self.config)
            disable_aiosmtp = self.config.getboolean('performance', 'disable_aiosmtp')
            print(fc.strcolor("INFO: ", "blue"), "config checked")
        except Exception as e:
            print(fc.strcolor('ERROR: ', "red"), f'failed to initialise bouncer: {str(e)}')
            import traceback
            traceback.print_exc()
            return False
        if HAVE_AIOSMTP:
            print(fc.strcolor("INFO: ", "blue"), "aiosmtplib available")
        return True
