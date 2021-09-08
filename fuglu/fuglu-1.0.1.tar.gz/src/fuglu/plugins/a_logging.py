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
from fuglu.shared import AppenderPlugin, apply_template, get_outgoing_helo, FileList, actioncode_to_string, FuConfigParser
from fuglu.stringencode import force_uString, force_bString
from fuglu.mailattach import NoExtractInfo
from fuglu.caching import smart_cached_memberfunc
import datetime
import re
import os
import json
import logging
import urllib
import urllib.parse
import hashlib
from domainmagic import extractor, tld
from domainmagic.mailaddr import strip_batv, decode_srs, domain_from_mail, split_mail
from domainmagic.validators import is_email
from domainmagic.validators import is_url_tldcheck


try:
    import elasticsearch
    HAVE_ELASTICSEARCH = True
except ImportError:
    elasticsearch = None
    HAVE_ELASTICSEARCH = False


FIELDMAP = {
    'id': 'fugluid',
    'injectqueueid': 'queueid',
    'Attachment.bounce.queueid': 'bounceqid'
}
LOG_EXCLUDE_FQDN=['www.w3.org', 'schemas.microsoft.com']
LOG_EXCLUDE_DOMAIN=['avast.com']

LOG_MAPPING = {
    "properties": {
        "headers": {"type": "nested"},
        "spamreport": {"type": "nested"},
        "virusreport": {"type": "nested"},
        "blockedreport": {"type": "nested"},
        "uris": {"type": "nested"},
        "attachments": {"type": "nested"},
    }
}



class URILogger(object):
    def __init__(self, config, section):
        self.logger = logging.getLogger('fuglu.plugins.logging.%s' % self.__class__.__name__)
        self.config = config
        self.section = section
        self.tldmagic = None
        self.extratlds = None
        self.extratlds_lastlist = None
        self._init_tldmagic()
    
        
    def _init_tldmagic(self):
        init_tldmagic = False
        extratlds = []
        
        if self.extratlds is None:
            extratldfile = self.config.get(self.section,'extra_tld_file')
            if extratldfile and os.path.exists(extratldfile):
                self.extratlds = FileList(extratldfile, lowercase=True)
                init_tldmagic = True
        
        if self.extratlds is not None:
            extratlds = self.extratlds.get_list()
            if self.extratlds_lastlist != extratlds: # extra tld file changed
                self.extratlds_lastlist = extratlds
                init_tldmagic = True
        
        if self.tldmagic is None or init_tldmagic:
            self.tldmagic = tld.TLDMagic()
            for t in extratlds: # add extra tlds to tldmagic
                self.tldmagic.add_tld(t)
                

    def _remove_uris_in_rcpt_domain(self, uris, to_domain, suspectid=None):
        if uris is None:
            return {}
        new_uris = {}
        for uri in uris.keys():
            try:
                u = urllib.parse.urlparse(uri)
            except Exception as e:
                # log error and skip on logging this uri on error
                self.logger.error(f"(uri from rcpt domain) {suspectid if suspectid else '<>'} msg: {str(e)} uri: {uri}")
                continue
        
            if u.hostname and (u.hostname == to_domain or u.hostname.endswith('.%s' % to_domain)):
                continue
            elif not u.hostname:
                self.logger.debug('%s not a parseable URL: %s' % (suspectid, uri))
            new_uris[uri] = uris.get(uri, 'unknown')
        return new_uris
    

    def _remove_uri_fragments(self, uris):
        new_uris = {}
        urikeys = list(uris.keys())
        for uri in urikeys:
            fragment = False
            for u in urikeys:
                if uri != u and uri in u:
                    fragment = True
                    break
            if not fragment:
                new_uris[uri] = uris.get(uri, 'unknown')
        return new_uris
    
    
    def _get_domain_from_fqdn(self, fqdn, suspect=None):
        try:
            self._init_tldmagic()
            domain = self.tldmagic.get_domain(fqdn).lower()
        except Exception as e:
            # log error
            self.logger.error(f"{suspect.id if suspect else '<>'} msg: {str(e)} fqdn: {fqdn}")
            return None
        return domain
    
    
    def _get_domain_from_uri(self, uri, suspect=None):
        try:
            fqdn = extractor.domain_from_uri(uri)
            if fqdn in LOG_EXCLUDE_FQDN:
                return None
        except Exception as e:
            # log error
            self.logger.error(f"{suspect.id if suspect else '<>'} msg: {str(e)} uri: {uri}")
            return None
        domain = self._get_domain_from_fqdn(fqdn, suspect)
        if domain in LOG_EXCLUDE_DOMAIN:
            return None
        return fqdn, domain


    def get_all_uris(self, suspect, maxitems):
        urilist = []
        tags = self.config.getlist(self.section, 'log_uri_tags')
        uris = {}
        for tag in tags:
            taguris = suspect.get_tag(tag, [])
            for uri in taguris:
                if uri not in uris and is_url_tldcheck(uri, exclude_fqdn=LOG_EXCLUDE_FQDN, exclude_domain=LOG_EXCLUDE_DOMAIN):
                    uris[uri] = tag
    
        uris = self._remove_uris_in_rcpt_domain(uris, suspect.to_domain, suspect.id)
        uris = self._remove_uri_fragments(uris)
        for rawuri in list(uris.keys())[:maxitems]:
            uri = extractor.redirect_from_url(rawuri)
            fqdn, domain = self._get_domain_from_uri(uri, suspect=suspect)
            if domain is None:
                self.logger.warning('%s failed to extract domain from uri %s' % (suspect.id, uri))
                continue
            logitem = {
                'type': 'uri',
                'fqdn': fqdn,
                'domain': domain,
                'uri': uri,
                'src': uris.get(rawuri, 'unknown')
            }
            urilist.append(logitem)
        return urilist
    
    
    def get_all_emails(self, suspect, maxitems):
        urilist = []
        tags = self.config.getlist(self.section, 'log_email_tags')
        emails = {}
        for tag in tags:
            tagaddrs = suspect.get_tag(tag, [])
            for addr in tagaddrs:
                if is_email(addr):
                    emails[addr] = tag
        
        for addr in list(emails.keys())[:maxitems]:
            if addr.startswith('//'):
                continue
            fqdn = domain_from_mail(addr)
            domain = self._get_domain_from_fqdn(fqdn, suspect)
            if domain is None:
                self.logger.warning('%s failed to extract domain from email address %s' % (suspect.id, addr))
                continue
            logitem = {
                'type': 'email',
                'fqdn': fqdn,
                'domain': domain,
                'uri': addr,
                'src': emails.get(addr, 'unknown')
            }
            urilist.append(logitem)
        return urilist


class AttLogger(object):
    def __init__(self, config, section):
        self.logger = logging.getLogger('fuglu.plugins.logging.%s' % self.__class__.__name__)
        self.config = config
        self.section = section
    
    
    def _skip_attachment_type(self, att_type):
        SKIPS = ['text/xml', 'text/json']
        for item in SKIPS:
            if att_type == item or att_type.startswith(item):
                return True
        return False
    
    
    def _skip_filename(self, filename):
        # found in .idab
        SKIP_RE = [re.compile('^LOG/[0-9]{1,20}\.DLF$')]
        for item in SKIP_RE:
            if item.match(filename):
                return True
        return False
    
    
    def get_all_attachments(self, suspect, maxitems=50):
        hashes = self.config.getlist(self.section,'log_attachment_hashes')
        attachments = []
        
        noextractinfo = NoExtractInfo()
        attachmentlist = suspect.att_mgr.get_objectlist(level=1, include_parents=True, noextractinfo=noextractinfo)
        attachmentcount = len(attachmentlist)
        
        noextractlist = noextractinfo.get_filtered(minus_filters=["level"])
        for item in noextractlist:
            self.logger.warning('%s extraction failed of file %s with message %s' % (suspect.id, item[0], item[1]))
        
        count = 0
        for attObj in attachmentlist:
            filename = attObj.location()
            if attachmentcount >= maxitems and attObj.in_archive and (self._skip_attachment_type(attObj.contenttype) or self._skip_filename(filename)):
                continue
            
            if count >= maxitems:
                break
            
            logitem = {
                'name': filename,
                'size': attObj.filesize or 0,
                'mime': attObj.contenttype,
                'is_inline': attObj.is_inline,
                'is_attachment': attObj.is_attachment,
                'is_archive': attObj.is_archive,
                'in_archive': attObj.in_archive,
            }
            for hashtype in hashes:
                logitem[hashtype] = attObj.get_checksum(hashtype)
            attachments.append(logitem)
            count += 1
        return attachments


class ElasticBackend(object):
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.logger = logging.getLogger('logging.%s' % self.__class__.__name__)
        self.elastic_connection = {}
    
    
    def get_elastic_connection(self):
        es = None
        elastic_uris = self.config.getlist(self.section,'elastic_uris')
        if elastic_uris:
            elastic_uri_string = ','.join(elastic_uris)
            try:
                es = self.elastic_connection[elastic_uri_string]
            except KeyError:
                es = elasticsearch.Elasticsearch(hosts=elastic_uris)
                self.elastic_connection = {elastic_uri_string:es}
        return es
    
    
    def get_elastic_index(self, suspect):
        indextmpl = self.config.get(self.section,'elastic_index')
        indexname = apply_template(indextmpl, suspect)
        return indexname
    

    @smart_cached_memberfunc(inputs=[])
    def _set_index_mapping(self, indexname):
        self.logger.info(f'checking mapping of index {indexname}')
        es = self.get_elastic_connection()
        exists = es.indices.exists(index=indexname)
        if exists:
            need_put = False
            mapping = es.indices.get_mapping(index=indexname)
            properties = mapping.get(indexname, {}).get('mappings', {}).get('properties', {})
            for key in LOG_MAPPING['properties']:
                if not LOG_MAPPING['properties'][key]['type'] == properties.get(key, {}).get('type'):
                    need_put = True
                    break
            if need_put:
                try:
                    r = es.indices.put_mapping(body=LOG_MAPPING, index=indexname)
                except elasticsearch.exceptions.ElasticsearchException as e:
                    r = {'exc': e.__class__.__name__, 'msg':str(e)}
                if r.get('acknowledged'):
                    self.logger.info(f'put new mapping to elastic index {indexname}')
                else:
                    self.logger.info(f'error putting new mapping to elastic index {indexname} : {str(r)}')
            else:
                self.logger.debug(f'no need to update mapping of elastic index {indexname}')
        else:
            try:
                log_mapping = {'mappings': LOG_MAPPING}
                r = es.indices.create(indexname, body=log_mapping)
            except elasticsearch.exceptions.ElasticsearchException as e:
                r = {'exc': e.__class__.__name__, 'msg':str(e)}
            if r.get('acknowledged'):
                self.logger.info(f'created new elastic index {indexname}')
            else:
                self.logger.info(f'error creating new elastic index {indexname} : {str(r)}')
    
    
    def log_to_elastic(self, suspect, logdata):
        logdata['timestamp'] = datetime.datetime.utcfromtimestamp(suspect.timestamp).isoformat()
        es = self.get_elastic_connection()
        indexname = self.get_elastic_index(suspect)
        self._set_index_mapping(indexname)
        result = {}
        r = es.index(index=indexname, id=suspect.id, body=logdata)
        for key in ['_id']:
            try:
                result[key] = r[key]
            except KeyError:
                self.logger.error('%s key %s not found in result %s' % (suspect.id, key, r))
        self.logger.info('%s indexed in elastic: %s' % (suspect.id, r))
        return result


class ElasticLogger(AppenderPlugin):
    """
    write fuglu log data directly to elasticsearch
    all data related to a suspect is written to one elasticsearch document, what data exactly will be logged can be configured to a certain degree
    if write to elasticsearch fails, optionally fallback logging to local json files can be enabled. these json files can later be reimported.
    """
    def __init__(self, config, section=None):
        AppenderPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'elastic_uris':{
                'default': '',
                'description':'comma separated list of ElasticSearch host definition (hostname, hostname:port, https://user:pass@hostname:port/)',
            },
            'elastic_index':{
                'default': 'fuglulog-${date}',
                'description':'Name of ElasticSearch index in which document will be stored. Template vars (e.g. ${to_domain} or ${date}) can be used.',
            },
            'log_headers':{
                'default': 'from:addr,to:addr,reply-to:addr,subject,subject:hash:md5,message-id',
                'description:': """
                    Name of message headers to log and extract.
                    Address headers support tags such as :addr or :name.
                    All header support tag hash:algo - algo must be one of hashlibs supported hash algorithms
                    All header names will be prefixed hdr_ in elastic document, - and : will be converted to _"""
            },
            'log_values': {
                'default': 'id,from_address,from_domain,from_localpart,queue_id,sasl_login,size,timestamp,to_address,to_domain,to_localpart',
                'description:': 'Name of suspect attribute values to log and extract. Some values will be renamed.'
            },
            'log_tags':{
                'default': 'injectqueueid,fuzor.digest,log.scanhost,log.decision,log.clienthelo,log.clientip,log.clienthostname,archived,Attachment.bounce.queueid,spf.result,dkim.result,arc.result,dmarc.result,log.real_from_address',
                'description:': 'Name of message tags to log and extract. Some tags will be renamed.'
            },
            'log_raw_headers': {
                'default': 'all',
                'description': 'log raw headers. set to "all" for all headers or comma separated list of header names to be logged'
            },
            'log_uris': {
                'default': '50',
                'description': 'log URI information (specify max number of URIs and email addresses to log, 0 to disable URI logging)'
            },
            'log_email_tags': {
                'default': 'body.emails',
                'description': 'log URIs listed in given tags'
            },
            'log_uri_tags': {
                'default': 'body.uris,uris.safelinks,headers.uris',
                'description': 'log URIs listed in given tags'
            },
            'log_attachments': {
                'default': '50',
                'description': 'log attachment information (specify max number of attachments to log, 0 to disable attachment logging)'
            },
            'log_attachment_hashes': {
                'default': 'md5,sha1',
                'description': 'log attachment checksums, specify any hash allowed by haslib: %s' % ','.join(hashlib.algorithms_available)
            },
            'extra_tld_file': {
                'default':'',
                'description':'path to file with extra TLDs (2TLD or inofficial TLDs)'
            },
            'fallback_logdir': {
                'default': '/usr/local/fuglu/maillog/',
                'description': 'path to directory where logs are stored in case of elasticsearch connection/indexing failure'
            }
        }
        self.urilogger = None
        self.attlogger = None
        self.elasticbackend = None
        
        
    def _init_components(self):
        if self.urilogger is None:
            self.urilogger = URILogger(self.config, self.section)
        if self.attlogger is None:
            self.attlogger = AttLogger(self.config, self.section)
        if self.elasticbackend is None:
            self.elasticbackend = ElasticBackend(self.config, self.section)
    
    
    def _normalise_fieldname(self, field_name):
        if field_name.startswith('log.'):
            field_name = field_name[4:]
        else:
            field_name = FIELDMAP.get(field_name, field_name)
            badchars = '-.:'
            for c in badchars:
                field_name = field_name.replace(c, '_')
        return field_name
    
    
    def _normalise_header(self, suspect, header_name, header_tag, header_value):
        header_name = header_name.lower()
        if header_tag is not None:
            header_tag = header_tag.lower()
            if header_tag.startswith('hash'):
                _, algo = header_tag.split(':')
                if algo in hashlib.algorithms_available:
                    hasher = getattr(hashlib, algo)
                    header_value = hasher(force_bString(header_value)).hexdigest()
                else:
                    self.logger.info('%s unsupported hash algorithm %s' % (suspect.id, algo))
            elif header_name in ['from', 'to', 'reply-to', 'sender']:
                try:
                    parsed_header = suspect.parse_from_type_header(header=header_name, validate_mail=True)
                    if parsed_header:
                        display, address = parsed_header[0]
                        if header_tag == 'addr':
                            header_value = address
                        elif header_tag == 'name':
                            header_value = display
                except Exception as e:
                    self.logger.warning('%s error extracting %s address: %s' % (suspect.id, header_name, str(e)))
                    header_value = None
        if header_name == 'message_id': # make sure all message ids get logged with leading and traling <> for normalised search
            if not header_value.startswith('<'):
                header_value = f'<{header_value}'
            if not header_value.endswith('>'):
                header_value = f'{header_value}>'
        
        return header_value
    
    
    def _get_suspect_header_data(self, suspect):
        logdata = {}
        msg_header_data = self.config.getlist(self.section, 'log_headers')
        msgrep = suspect.get_message_rep()
        for header_name_tag in msg_header_data:
            if ':' in header_name_tag:
                header_name, header_tag = header_name_tag.split(':',1)
            else:
                header_tag = None
                header_name = header_name_tag
            header_value = msgrep.get(header_name)
            if header_value:
                header_value = self._normalise_header(suspect, header_name, header_tag, header_value)
                header_name = self._normalise_fieldname(f'hdr_{header_name_tag}')
                logdata[header_name] = header_value
        return logdata
    
    
    def _get_suspect_fields(self, suspect):
        logdata = {}
        suspect_fields = self.config.getlist(self.section, 'log_values')
        for field in suspect_fields:
            try:
                value = getattr(suspect, field)
                key = self._normalise_fieldname(FIELDMAP.get(field, field))
                logdata[key] = force_uString(value)
            except AttributeError:
                self.logger.debug('%s no suspect attribute %s' % (suspect.id, field))
        return logdata
    
    
    def _get_suspect_funcs(self, suspect):
        logdata = {}
        status = suspect.get_status()
        for func_name in status:
            key = self._normalise_fieldname(FIELDMAP.get(func_name, func_name))
            logdata[key] = status[func_name]
        return logdata
    
    
    def _get_suspect_tags(self, suspect):
        logdata = {}
        suspect_tags = self.config.getlist(self.section, 'log_tags')
        for tag in suspect_tags:
            value = suspect.get_tag(tag)
            if value is not None:
                key = self._normalise_fieldname(FIELDMAP.get(tag, tag))
                logdata[key] = force_uString(value)
        return logdata
    
    
    def _get_raw_headers(self, suspect, header_names):
        allhdr = header_names[0] == 'all'
        headerdata = []
        hdrline = 0
        msgrep = suspect.get_message_rep()
        headers = msgrep.items()
        hdrlines = len(headers)
        for hdr_name, hdr_content in headers:
            hdr_name_low = hdr_name.lower()
            if not (allhdr or hdr_name_low in header_names):
                continue
            hdrline += 1
            hdrdata = {}
            hdrdata['headerlines'] = hdrlines # how many lines will be written in log
            hdrdata['line'] = hdrline # current line number
            hdrdata['header'] = hdr_name
            hdrdata['iheader'] = hdr_name_low
            hdrdata['content'] = force_uString(hdr_content)
            headerdata.append(hdrdata)
        return headerdata
    
    
    def _get_virus_reports(self, suspect):
        logdata = []
        engines = suspect.get_tag('virus', {})
        for engine in engines.keys():
            if engines[engine]:
                virusreport = suspect.get_tag('%s.virus' % engine)
                for item in virusreport:
                    logitem = {}
                    logitem['engine'] = engine
                    logitem['file'] = item
                    logitem['virus'] = virusreport[item]
                    logdata.append(logitem)
        return logdata
    
    
    def _get_blocked_reports(self, suspect):
        logdata = []
        engines = suspect.get_tag('blocked', {})
        for engine in engines.keys():
            if engines[engine]:
                blockreport = suspect.get_tag('%s.blocked' % engine)
                for item in blockreport:
                    logitem = {}
                    logitem['engine'] = engine
                    logitem['file'] = item
                    logitem['blockinfo'] = blockreport[item]
                    logdata.append(logitem)
        return logdata
    
    
    def _get_spam_reports(self, suspect):
        logdata = []
        engines = suspect.get_tag('spam', {})
        for engine in engines.keys():
            if engines[engine]:
                logitem = {}
                logitem['spam'] = suspect.get_tag('spam', {}).get(engine, False)
                logitem['highspam'] = suspect.get_tag('highspam', {}).get(engine, False)
                logitem['report'] = force_uString(suspect.get_tag(f'{engine}.report'))
                for key in ['score', 'skipreason', 'stripped']:
                    value = suspect.get_tag(f'{engine}.{key}')
                    if value:
                        logitem[key] = value
                logdata.append(logitem)
        return logdata
    
    
    def _get_log_coredata(self, suspect):
        logdata = {}
        logdata.update(self._get_suspect_fields(suspect))
        logdata.update(self._get_suspect_funcs(suspect))
        logdata.update(self._get_suspect_tags(suspect))
        logdata.update(self._get_suspect_header_data(suspect))
        
        header_names = self.config.getlist(self.section, 'log_raw_headers')
        headers = self._get_raw_headers(suspect, header_names)
        if headers:
            logdata['headers'] = headers
            
        spamreport = self._get_spam_reports(suspect)
        if spamreport:
            logdata['spamreport'] = spamreport
            
        virusreport = self._get_virus_reports(suspect)
        if virusreport:
            logdata['virusreport'] = virusreport
            
        blockreport = self._get_blocked_reports(suspect)
        if blockreport:
            logdata['blockedreport'] = virusreport
        
        maxatt = self.config.getint(self.section, 'log_attachments')
        if maxatt > 0:
            att = self.attlogger.get_all_attachments(suspect, maxatt)
            if att:
                logdata['attachments'] = att
        
        maxuri = self.config.getint(self.section, 'log_uris')
        if maxuri > 0:
            uris = self.urilogger.get_all_uris(suspect, maxuri)
            emails = self.urilogger.get_all_emails(suspect, maxuri)
            uris.extend(emails)
            if uris:
                logdata['uris'] = uris
        
        return logdata
    
    
    def _log_to_file(self, suspect, logdata):
        dirpath = self.config.get(self.section, 'fallback_logdir')
        if dirpath:
            indexname = self.elasticbackend.get_elastic_index(suspect)
            filename = f'{suspect.id}.json'
            indexpath = os.path.join(dirpath, indexname)
            filepath = os.path.join(indexpath, filename)
            try:
                jsondata = json.dumps(logdata)
                if not os.path.exists(indexpath):
                    os.mkdir(indexpath)
                with open(filepath) as f:
                    f.write(jsondata)
                self.logger.info('%s dumped %s bytes of json data to %s' % (suspect.id, len(jsondata), filepath))
            except Exception as e:
                self.logger.error('%s failed to dump json data to %s due to %s' % (suspect.id, filepath, str(e)))
    
    
    def _normalise_address(self, address):
        address = strip_batv(address)
        address = decode_srs(address)
        return address
    
    
    def _add_tags(self, suspect, decision=None):
        suspect.set_tag('log.scanhost', get_outgoing_helo(self.config))
        
        if decision is not None:
            suspect.set_tag('log.decision', actioncode_to_string(decision))
        
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            clienthelo, clientip, clienthostname = clientinfo
            suspect.set_tag('log.client_helo', clienthelo)
            suspect.set_tag('log.client_ip', clientip)
            suspect.set_tag('log.client_hostname', clienthostname)
        
        if suspect.from_address:
            try:
                real_from_address = self._normalise_address(suspect.from_address)
                real_from_localpart, real_from_domain = split_mail(real_from_address)
                suspect.set_tag('log.real_from_address', real_from_address)
                suspect.set_tag('log.real_from_domain', real_from_domain)
                suspect.set_tag('log.real_from_localpart', real_from_localpart)
            except Exception as e:
                self.logger.warning('%s could not normalise address %s error was %s' % (suspect.id, suspect.from_address, str(e)))
    
    
    def process(self, suspect, decision):
        self._init_components()
        if self.elasticbackend.get_elastic_connection() is None:
            return
        self._add_tags(suspect, decision)
        logdata = self._get_log_coredata(suspect)
        try:
            result = self.elasticbackend.log_to_elastic(suspect, logdata)
            self.logger.info('%s processed with result %s' % (suspect.id, result))
        except Exception as e:
            self.logger.error('%s failed to index in elastic due to %s' % (suspect.id, str(e)))
            self._log_to_file(suspect, logdata)
    
    
    def lint(self):
        if not HAVE_ELASTICSEARCH:
            print('ERROR: elasticsearch library not available')
            return False
    
        print('INFO: Elasticsearch library version: %s' % elasticsearch.__versionstr__)
        
        self._init_components()
        es = self.elasticbackend.get_elastic_connection()
        if es is None:
            print('WARNING: elastic_uris not defined, this plugin will do nothing')
            return False
        elif not es.ping():
            print('ERROR: failed to connect to elasticsearch')
            return False
        
        dirpath = self.config.get(self.section, 'fallback_logdir')
        if dirpath and not os.path.exists(dirpath):
            print('ERROR: fallback logdir %s does not exist' % dirpath)
            return False

        invalid_hashes = [h for h in self.config.getlist(self.section, 'log_attachment_hashes') if h not in hashlib.algorithms_available]
        if invalid_hashes:
            print('ERROR: invalid hash algorithms in log_attachment_hashes: %s' % ','.join(invalid_hashes))
            return False
    
        return True


class ElasticImport(object):
    def __init__(self, configfile):
        self.config = FuConfigParser()
        if os.path.exists(configfile):
            self.config.read_file(configfile)
        else:
            print(f'ERROR: no such config {configfile}')
        self.section = self.__class__.__name__
        self.backend = ElasticBackend(self.config, 'ElasticLogger')
    
    
    def _log_to_elastic(self, indexname, suspectid, logdata):
        es = self.backend.get_elastic_connection()
        self.backend._set_index_mapping(indexname)
        success = True
        r = es.index(index=indexname, id=suspectid, body=logdata)
        if not '_id' in r:
            print('%s key _id not found in result %s' % (suspectid, r))
            success = False
        print('%s indexed in elastic: %s' % (suspectid, r))
        return success
    
    
    def load_files(self, cleanup=True):
        dirpath = self.config.get(self.section, 'fallback_logdir')
        if not dirpath:
            print('fallback_logdir not set, nothing to do')
        else:
            for indexname, _, filenames in os.walk(dirpath):
                for filename in filenames:
                    if filename.endswith('.json'):
                        suspectid = filename.rsplit('.')[0]
                        filepath = os.path.join(dirpath, indexname, filename)
                        with open(filepath) as fp:
                            filecontent = json.load(fp)
                        success = self._log_to_elastic(indexname, suspectid, filecontent)
                        if success and cleanup:
                            os.remove(filepath)
            if cleanup:
                self._cleanup_dirs(dirpath)
                        
    
    def _cleanup_dirs(self, dirpath):
        for indexname, _, filenames in os.walk(dirpath):
            if not filenames:
                abspath = os.path.join(dirpath, indexname)
                os.rmdir(abspath)
    

if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--mapping', help='print elastic index mapping and quit', action='store_true')
    parser.add_argument('--import', help='import json files stored in fallback_logdir. expects path to config file as argument', default='/etc/fuglu/conf.d/logging.conf')
    parser.add_argument('--keepfiles', help='do not remove files that were imported successfully', action='store_true')
    args = parser.parse_args()
    importconfig = getattr(args, 'import')
    
    if args.mapping:
        print('Logger indices mapping:')
        print(json.dumps(LOG_MAPPING))
        sys.exit(0)
    elif importconfig:
        elimp = ElasticImport(importconfig)
        elimp.load_files(not args.keepfiles)
        
        
