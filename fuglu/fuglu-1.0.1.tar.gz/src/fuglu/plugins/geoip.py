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
#
from fuglu.shared import ScannerPlugin,DUNNO
from geoip2 import database
import os



class GeoIPLookup(ScannerPlugin):
    
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'headername': {
                'default': 'X-Geo-Country',
                'description': 'header name',
            },
            'database': {
                'default': '',
                'description': 'path to geoip database',
            },
        }
        self.geoip = None
    
    
    def _init_geoip(self):
        filename = self.config.get(self.section, 'database')
        if self.geoip is None and filename:
            if os.path.exists(filename):
                self.geoip = database.Reader(filename)
    
    
    def _get_clientip(self, suspect):
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            helo, clientip, clienthostname = clientinfo
        else:
            helo, clientip, clienthostname = None, None, None
        return clientip
    
    
    def _get_countrycode(self, clientip):
        cc = None
        try:
            data = self.geoip.country(clientip)
            cc = data.country.iso_code
            cc = cc.lower()
        except Exception:
            pass
        return cc
    
    
    def examine(self, suspect):
        self._init_geoip()
        
        if self.geoip is not None:
            clientip = self._get_clientip(suspect)
            if clientip is not None:
                cc = self._get_countrycode(clientip)
                if cc is not None:
                    headername = self.config.get(self.section, 'headername')
                    suspect.write_sa_temp_header(headername, cc)
                    suspect.set_tag('geoip.countrycode', cc)
        
        return DUNNO
    
    
    def lint(self):
        ok = self.check_config()
        if ok:
            filename = self.config.get(self.section, 'database')
            if not os.path.exists(filename):
                print('ERROR: Could not find geoip database %s' % filename)
                ok = False
            else:
                self._init_geoip()
                if self.geoip is None:
                    print('ERROR: geoip not initialized')
                    ok = False
                else:
                    checks = [('8.8.8.8', 'us')]
                    for ip, expcc in checks:
                        cc = self._get_countrycode(ip)
                        if cc != expcc:
                            print(f'ERROR: IP={ip} did not get expected={expcc} got={cc}')
                            ok = False
        return ok