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

#
from fuglu.shared import ScannerPlugin, DUNNO, DELETE, string_to_actioncode, SuspectFilter
from fuglu.extensions.sql import DBConfig
import os
import re



class KillerPlugin(ScannerPlugin):

    """DELETE all mails (for special mail setups like spam traps etc)"""

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()

    def __str__(self):
        return "delete Message"

    def examine(self, suspect):
        return DELETE

    def lint(self):
        print("""!!! WARNING: You have enabled the KILLER plugin - NO message will forwarded to postfix. !!!""")
        return True



class FilterDecision(ScannerPlugin):
    """
    Evaluates possible decision based on results by previous plugins e.g.
    - check results of antivirus scanners
    - check results of spam analyzers
    - archive/quarantine status
    - block/welcomelist or filter settings
    and adds headers or subject tags according to filter result. Will decide if mail should be delivered or deleted.
    """
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'testmode': {
                'default': 'False',
                'description': 'will not delete any mail if set to True',
            },
        }
    
    
    def __str__(self):
        return "Filter Decision"
    
    
    def lint(self):
        allok = self.check_config()
        if self.config.get(self.section, 'testmode'):
            print('WARNING: testmode active, will not delete any mail. may forward untagged spam or malware!')
        return allok
    
    
    def _get_filtersetting(self, suspect, option, default=None):
        return suspect.get_tag('filtersettings', {}).get(option, default)
    
    
    def _subject_updater(self, subject, **params):
        tag = params.get('tag')
        if tag:
            subject = '%s %s' % (tag, subject)
        return subject
    
    
    def _add_subject_tag_ext(self, suspect):
        subject_tag_level = int(self._get_filtersetting(suspect, 'subject_tag_ext_level', 0))
        if subject_tag_level == 0:
            return
        
        do_tag = False
        if subject_tag_level == 2:
            if suspect.from_domain == suspect.to_domain:
                do_tag = True
            else:
                hdr_from_address = suspect.parse_from_type_header(header='From', validate_mail=True)
                if hdr_from_address and hdr_from_address[0]:
                    hdr_from_domain = hdr_from_address[0][1].rsplit('@',1)[-1]
                    if hdr_from_domain.lower() == suspect.to_domain:
                        do_tag = True
        elif subject_tag_level == 1:
            do_tag = True
        
        subject_tag = self._get_filtersetting(suspect, 'subject_tag_ext')
        if do_tag and subject_tag:
            suspect.update_subject(self._subject_updater, tag=subject_tag)
        if do_tag:
            prependaddedheaders = self.config.get('main', 'prependaddedheaders')
            suspect.add_header(f'{prependaddedheaders}External', 'yes')
    
    
    def _add_subject_tag_status(self, suspect):
        prependaddedheaders = self.config.get('main', 'prependaddedheaders')
        if suspect.is_virus():
            suspect.add_header(f'{prependaddedheaders}Virus', 'yes')
        elif suspect.is_blocklisted():
            suspect.add_header(f'{prependaddedheaders}Blocklisted', 'yes')
        elif suspect.is_welcomelisted():
            suspect.add_header(f'{prependaddedheaders}Welcomelisted', 'yes')
        elif suspect.is_blocked():
            suspect.add_header(f'{prependaddedheaders}Blocked', 'yes')
        elif suspect.is_spam():
            suspect.add_header(f'{prependaddedheaders}Spam', 'yes')
            subject_tag_spam = self._get_filtersetting(suspect, 'subject_tag_spam')
            if subject_tag_spam:
                suspect.update_subject(self._subject_updater, tag=subject_tag_spam)
        elif suspect.is_highspam():
            suspect.add_header(f'{prependaddedheaders}HighSpam', 'yes')
    
    
    def _check_deliver_spam(self, suspect):
        deliver = True
        if suspect.is_spam():
            deliver = False
            if self._get_filtersetting(suspect, 'deliver_spam', False):
                deliver = True
        elif suspect.is_highspam():
            deliver = False
            if self._get_filtersetting(suspect, 'deliver_highspam', False):
                deliver = True
        
        if not suspect.is_ham() and not deliver and suspect.get_tag('archived', False):
            deliver = True
        
        if not suspect.is_ham() and deliver:
            spam_recipient = self._get_filtersetting(suspect, 'spam_recipient')
            if spam_recipient:
                suspect.to_address = spam_recipient
        return deliver
    
    
    def examine(self, suspect):
        deliver = self._check_deliver_spam(suspect)
        if not deliver:
            if self.config.get(self.section, 'testmode'):
                self.logger.info('%s testmode enabled. else would be deleting due to filterdecision')
                return DUNNO
            else:
                self.logger.info('%s deleting due to filterdecision')
                return DELETE
        
        if not suspect.is_ham():
            self._add_subject_tag_status(suspect)
        else:
            self._add_subject_tag_ext(suspect)
        return DUNNO



class ActionOverridePlugin(ScannerPlugin):

    """
    Override actions based on a Suspect Filter file.
    For example, delete all messages from a specific sender domain.
    """

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'actionrules': {
                'default': '${confdir}/actionrules.regex',
                'description': 'Rules file',
            }
        }
        self.filter = None
    
    
    def __str__(self):
        return "Action Override"
    
    
    def lint(self):
        allok = self.check_config() and self.lint_filter()
        return allok
    
    
    def lint_filter(self):
        filterfile = self.config.get(self.section, 'actionrules')
        sfilter = SuspectFilter(filterfile)
        return sfilter.lint()
    
    
    def examine(self, suspect):
        actionrules = self.config.get(self.section, 'actionrules')
        if actionrules is None or actionrules == "":
            return DUNNO

        if not os.path.exists(actionrules):
            self.logger.error('Action Rules file does not exist : %s' % actionrules)
            return DUNNO

        if self.filter is None:
            self.filter = SuspectFilter(actionrules)

        (match, arg) = self.filter.matches(suspect)
        if match:
            if arg is None or arg.strip() == '':
                self.logger.error("Rule match but no action defined.")
                return DUNNO

            arg = arg.strip()
            spl = arg.split(None, 1)
            actionstring = spl[0]
            message = None
            if len(spl) == 2:
                message = spl[1]
            self.logger.debug("%s: Rule match! Action override: %s" % (suspect.id, arg.upper()))

            actioncode = string_to_actioncode(actionstring, self.config)
            if actioncode is not None:
                return actioncode, message

            elif actionstring.upper() == 'REDIRECT':
                suspect.to_address = message.strip()
                # todo: check for invalid adress, multiple adressses, set suspect.recipients instead of to_address
                # todo: document redirect action
            else:
                self.logger.error("Invalid action: %s" % arg)
                return DUNNO

        return DUNNO



class RcptRewrite(ScannerPlugin):
    """
    This plugin reads a new recipient from some header.
    For safety reasons it is recommended to set the header name to a random value and remove the header in postfix after reinjection.
    """
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        
        self.requiredvars = {
            'headername': {
                'default': 'X-Fuglu-Redirect',
                'description': 'name of header indicating new recipient',
            },
        }
    
    
    def examine(self, suspect):
        headername = self.config.get(self.section, 'headername')
        msgrep = suspect.get_message_rep()
        newlhs = msgrep.get(headername, None)
        
        # get from mime headers
        if newlhs is None and msgrep.is_multipart():
            for part in msgrep.walk():
                newlhs = part.get(headername, None)
                if newlhs is not None:
                    break
        
        if newlhs is None:
            self.logger.debug(f'{suspect.id} nothing to rewrite')
            return DUNNO
        
        rcptdom = suspect.to_address.rsplit('@',1)[-1]
        newrcpt = f'{newlhs}@{rcptdom}'
        self.logger.info(f'{suspect.id} rcpt rewritten from {suspect.to_address} to {newrcpt}')
        suspect.to_address = newrcpt
        suspect.recipients = [newrcpt]
        return DUNNO



class ConditionalRcptAppend(ScannerPlugin):
    """
    Append domain name to recipient based on subject patterns
    """
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'rcpt_append': {
                'default': '',
                'description': 'domain name to append to recipient',
            },
            'subject_rgx': {
                'default': '',
                'description': 'regular expression pattern for subject matches. rewrite only if regex hits.',
            },
            'enable_cond_rewrite': {
                'default': 'False',
                'description': 'enable rewrite feature',
            }
        }
    
    
    def _rewrite_rcpt(self, rcpt, append):
        if not rcpt.endswith(append):
            rcpt = f'{rcpt}{append}'
        return rcpt
        
        
    def examine(self, suspect):
        rcpt_append = self.config.get(self.section, 'rcpt_append')
        subject_rgx = self.config.get(self.section, 'subject_rgx')
        if not rcpt_append or not subject_rgx:
            return DUNNO
        
        runtimeconfig = DBConfig(self.config, suspect)
        enabled = runtimeconfig.getboolean(self.section, 'enable_cond_rewrite')
        if not enabled:
            return DUNNO
        
        subject = suspect.get_message_rep().get('subject','')
        if subject and re.search(subject_rgx, subject):
            if not rcpt_append.startswith('.'):
                rcpt_append = f'.{rcpt_append}'
            newrcpt = self._rewrite_rcpt(suspect.to_address, rcpt_append)
            self.logger.info(f'{suspect.id} rewrite rcpt {suspect.to_address} to {newrcpt}')
            suspect.to_address = newrcpt
        
            recipients = []
            for addr in suspect.recipients:
                newaddr = self._rewrite_rcpt(addr, rcpt_append)
                if not newaddr == newrcpt:
                    self.logger.debug(f'{suspect.id} rewrite rcpt {addr} to {newrcpt}')
                recipients.append(newaddr)
            suspect.recipients = recipients
        else:
            self.logger.debug(f'{suspect.id} no rewrite subject tags found')
        return DUNNO
        
        
    
    
    
    