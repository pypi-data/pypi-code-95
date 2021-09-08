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

import typing as tp
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, get_domain_setting
from fuglu.mshared import BMPEOBMixin, BasicMilterPlugin
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from fuglu.stringencode import force_uString
from fuglu.shared import _SuspectTemplate, get_default_cache


class MessageSize(BMPEOBMixin, BasicMilterPlugin):
    
    """
    This plugin allows setting individual message size limits per recipient domain
    """
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars={
            'dbconnection':{
                'default':"mysql://root@localhost/config?charset=utf8",
                'description':'SQLAlchemy Connection string. Leave empty to disable SQL lookups',
            },
            'domain_sql_query':{
                'default':"SELECT max_size from domain where domain_name=:domain",
                'description':'get from sql database :domain will be replaced with the actual domain name. must return field max_size',
            },
            'messagetemplate':{
                'default':'message size ${msg_size} exceeds size limit ${max_size} of recipient domain ${to_domain}',
                'description':'reject message template for policy violators'
            },
            'state': {
                'default': asm.EOB,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    def _get_domain_limit(self, to_domain):
        max_size = None
        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        sqlquery = self.config.get(self.section, 'domain_sql_query')

        # use DBConfig instead of get_domain_setting
        if dbconnection!='' and SQL_EXTENSION_ENABLED:
            cache = get_default_cache()
            max_size = get_domain_setting(to_domain, dbconnection, sqlquery, cache, self.section, False, self.logger)
        
        return max_size



    def examine_eob(self, sess: tp.Union[sm.MilterSession, asm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        if not SQL_EXTENSION_ENABLED:
            return sm.CONTINUE

        recipients = force_uString(sess.recipients)
        recipients = [r for r in recipients if r]

        if not recipients:
            self.logger.error(f'{sess.id} No TO address found')
            return sm.CONTINUE
        
        try:
            msg_size = sess.size
        except (ValueError, TypeError):
            msg_size = 0
        
        if msg_size == 0:
            self.logger.debug(f'{sess.id} skipped: message size unknown (not specified or not in end-of-data restrictions)')
            return sm.CONTINUE

        # unique list of domains for recipients
        to_domains = list(set([sm.MilterSession.extract_domain(r) for r in recipients]))

        max_size_reduced = None

        for to_domain in to_domains:
            max_size = self._get_domain_limit(to_domain)

            if max_size:
                if max_size_reduced is None:
                    max_size_reduced = max_size
                else:
                    #max_size_reduced = min(max_size, max_size_reduced)
                    # use maximum to see if someone can receive...
                    max_size_reduced = max(max_size, max_size_reduced)

        if max_size_reduced is None or max_size_reduced==0:
            self.logger.debug(f'{sess.id} skipped: no max size for domain{"s" if len(to_domains) > 1 else ""} {to_domains} specified')
            return sm.CONTINUE

        if msg_size > max_size_reduced:
            template = _SuspectTemplate(self.config.get(self.section, 'messagetemplate'))
            templ_dict = sess.get_templ_dict()
            templ_dict['msg_size'] = msg_size
            templ_dict['max_size'] = max_size_reduced
            message = template.safe_substitute(templ_dict)

            return sm.REJECT, message

        return sm.CONTINUE


    def lint(self, state=None) -> bool:
        if state and state not in self.state:
            # not active in current state
            return True

        if not SQL_EXTENSION_ENABLED:
            print("sqlalchemy is not installed")
            return False
    
        if not self.checkConfig():
            return False
        
        try:
            dbconnection = self.config.get(self.section, 'dbconnection')
            conn=get_session(dbconnection)
            conn.execute("SELECT 1")
        except Exception as e:
            print("Failed to connect to SQL database: %s" % str(e))
            return False
            
        return True
        
        
        
        
    