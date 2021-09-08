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
from fuglu.shared import ScannerPlugin, DUNNO, SuspectFilter, apply_template, get_outgoing_helo, Suspect
from fuglu.stringencode import force_uString, force_bString
import os
import shutil
import pwd
import grp
import logging
import time
import smtplib
import socket
import datetime
from collections import OrderedDict

try:
    from cassandra.cluster import Cluster
    from cassandra.policies import RoundRobinPolicy
    HAVE_CASSANDRA = True
except ImportError:
    HAVE_CASSANDRA = False
    
try:
    import elasticsearch
    HAVE_ELASTICSEARCH = True
except ImportError:
    HAVE_ELASTICSEARCH = False



class AbstractBackend(object):
    requiredvars = {}
    
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.logger = logging.getLogger('fuglu.archive.backend.%s' % self.__class__.__name__)
    
    def __str__(self):
        return self.__class__.__name__
        
    def archive(self, suspect, fugluid_override=None):
        raise NotImplementedError
    
    def lint(self):
        raise NotImplementedError
    
    def _get_msg_source(self, suspect, original=True):
        if original:
            content = suspect.get_original_source()
        else:
            content = suspect.get_source()
        return content



class LocalDirBackend(AbstractBackend):
    """
    This is the default backend. It stores mail in a local directory.
    Status: Mature
    """
    requiredvars = {
        'local_archivedir': {
            'default': '/tmp',
            'description': 'storage for archived messages',
        },
        'local_subdirtemplate': {
            'default': '${to_domain}/${to_localpart}/${date}',
            'description': 'subdirectory within archivedir',
        },
        'local_filenametemplate': {
            'default': '${archiveid}.eml',
            'description': 'filename template for the archived messages',
        },
        'local_useoriginal': {
            'default': 'True',
            'description': "if true/1/yes: store original message\nif false/0/no: store message probably altered by previous plugins, eg with spamassassin headers",
        },
        'local_chown': {
            'default': '',
            'description': "change owner of saved messages (username or numeric id) - this only works if fuglu is running as root (which is NOT recommended)",
        },
        'local_chgrp': {
            'default': '',
            'description': "change group of saved messages (groupname or numeric id) - the user running fuglu must be a member of the target group for this to work",
        },
        'local_chmod': {
            'default': '',
            'description': "set file permissions of saved messages",
        },
    }
    
    
    def archive(self, suspect, fugluid_override=None):
        archivedir = self.config.get(self.section, 'local_archivedir')
        if archivedir == "":
            self.logger.error('Archivedir is not specified')
            return
        
        subdirtemplate = self.config.get(self.section, 'local_subdirtemplate')
        
        # the archive root dir
        startdir = os.path.abspath(archivedir)
        
        # relative dir within archive root
        subdir = apply_template(subdirtemplate, suspect)
        if subdir.endswith('/'):
            subdir = subdir[:-1]
        if subdir.startswith('/'):
            subdir = subdir[1:]
        
        # filename without dir
        filenametemplate = self.config.get(self.section, 'local_filenametemplate')
        
        values = {
            'archiveid': fugluid_override or suspect.id,
        }
        filename = apply_template(filenametemplate, suspect, values)
        # make sure filename can't create new folders
        filename = filename.replace('/', '_')
        
        # absolute final filepath
        requested_path = os.path.join(startdir, subdir, filename)
        
        finaldir = os.path.dirname(requested_path)
        if not os.path.isdir(finaldir):
            os.makedirs(finaldir, 0o755)
        
        if self.config.getboolean(self.section, 'local_useoriginal'):
            shutil.copy(suspect.tempfile, requested_path)
        else:
            with open(requested_path, 'wb') as fp:
                # write bytes
                fp.write(suspect.get_source())
        
        chmod = self.config.get(self.section, 'local_chmod')
        chgrp = self.config.get(self.section, 'local_chgrp')
        chown = self.config.get(self.section, 'local_chown')
        if chmod or chgrp or chown:
            self._setperms(requested_path, chmod, chgrp, chown)
        
        self.logger.info('Message from %s to %s archived as %s' % (
            suspect.from_address, suspect.to_address, requested_path))
        return dict(filepath=requested_path)
    

    def lint(self):
        archivedir = self.config.get(self.section, 'local_archivedir')
        if archivedir == "":
            print('Archivedir is not specified')
            return False
    
        if not os.path.isdir(archivedir):
            print("Archivedir '%s' does not exist or is not a directory" % archivedir)
            return False
    
        return True
    
    
    def _setperms(self, filename, chmod, chgrp, chown):
        """Set file permissions and ownership
        :param filename The target file
        :param chmod string representing the permissions (example '640')
        :param chgrp groupname or group id of the target group. the user running fuglu must be a member of this group for this to work
        :param chown username or user id of the target user. fuglu must run as root for this to work (which is not recommended for security reasons)
        """
        
        # chmod
        if chmod:
            perm = int(chmod, 8)
            try:
                os.chmod(filename, perm)
            except Exception:
                self.logger.error('could not set permission on file %s' % filename)
        
        # chgrp
        changetogroup = -1
        if chgrp:
            group = None
            try:
                group = grp.getgrnam(chgrp)
            except KeyError:
                pass
            
            if group is None:
                try:
                    group = grp.getgrgid(int(chgrp))
                except (KeyError, ValueError):
                    pass
            
            if group is not None:
                changetogroup = group.gr_gid
            else:
                self.logger.warning("Group %s not found" % chgrp)
        
        # chown
        changetouser = -1
        if chown:
            user = None
            try:
                user = pwd.getpwnam(chown)
            except KeyError:
                pass
            
            if user is None:
                try:
                    user = pwd.getpwuid(int(chown))
                except (KeyError, ValueError):
                    pass
            
            if user is not None:
                changetouser = user.pw_uid
            else:
                self.logger.warning("User %s not found" % chown)
        
        if changetogroup != -1 or changetouser != -1:
            try:
                os.chown(filename, changetouser, changetogroup)
            except Exception as e:
                self.logger.error("Could not change user/group of file %s : %s" % (filename, str(e)))


class ElasticBackend(AbstractBackend):
    """
    This backend stores mail in ElasticSearch.
    Status: experimental
    """
    requiredvars = {
        'elastic_uris':{
            'default': '',
            'description':'comma separated list of ElasticSearch host definition (hostname, hostname:port, https://user:pass@hostname:port/)',
        },
        'elastic_index':{
            'default': 'fugluquar-${date}',
            'description':'Name of ElasticSearch index in which document will be stored. Template vars (e.g. ${to_domain} or ${date}) can be used.',
        },
        'elastic_extrafields':{
            'default':'',
            'description':'comma separated list of additional fields to be added to document. Any fuglu Suspect variable is permitted (e.g. to_address)',
        },
        'elastic_useoriginal': {
            'default': 'True',
            'description': """should we store the original message as retreived from postfix or store the
                                current state in fuglu (which might have been altered by previous plugins)""",
        },
    }
    elastic_connection = {}


    def get_elastic_connection(self):
        es = None
        elastic_uris = self.config.getlist(self.section, 'elastic_uris')
        if elastic_uris:
            elastic_uri_string = ','.join(elastic_uris)
            try:
                es = self.elastic_connection[elastic_uri_string]
            except KeyError:
                es = elasticsearch.Elasticsearch(hosts=elastic_uris)
                self.elastic_connection = {elastic_uri_string: es}
        return es
    
    
    def _get_elastic_index(self, suspect):
        indextmpl = self.config.get(self.section,'elastic_index')
        indexname = apply_template(indextmpl, suspect)
        return indexname
    
    
    def archive(self, suspect, fugluid_override=None):
        original = self.config.getboolean(self.section, 'elastic_useoriginal')
        content = self._get_msg_source(suspect, original)
        doc = {
            'fugluid': fugluid_override or suspect.id,
            'fugluid_original': fugluid_override or suspect.id,
            'content': force_uString(content),
            'timestamp': datetime.datetime.utcfromtimestamp(suspect.timestamp),
        }
        
        extrafields = self.config.getlist(self.section, 'elastic_extrafields')
        for field in extrafields:
            doc[field] = apply_template('${%s}' % field, suspect)
        
        es = self.get_elastic_connection()
        indexname = self._get_elastic_index(suspect)
        result = {}
        r = es.index(index=indexname, id=suspect.id, body=doc)
        for key in ['_id']:
            try:
                result[key] = r[key]
            except KeyError:
                self.logger.error('%s key %s not found in result %s' % (suspect.id, key, r))
        self.logger.info('%s indexed in elastic: %s' % (suspect.id, r))
        return result
    
    
    def lint(self):
        if not HAVE_ELASTICSEARCH:
            print('ERROR: elasticsearch library not available')
            return False
        
        print('INFO: Elasticsearch library version: %s' % elasticsearch.__versionstr__)
        
        es = self.get_elastic_connection()
        if not es.ping():
            print('ERROR: failed to connect to elasticsearch')
            return False
        
        return True
        


class CassandraBackend(AbstractBackend):
    """
    This backend stores mail in an Apache Cassandra database cluster.
    Status: abandoned (last used in 2018)
    """
    requiredvars = {
        'cassandra_hosts':{
            'default': '',
            'description':"quarantine cassandra hostnames, separated by comma",
        },
        'cassandra_keyspace':{
            'default': 'fugluquar',
            'description':"quarantine cassandra keyspace",
        },
        'cassandra_ttl':{
            'default': str(14*24*3600),
            'description':"ttl for quarantined files in seconds",
        },
        'cassandra_useoriginal': {
            'default': 'True',
            'description': """should we store the original message as retreived from postfix or store the
                                current state in fuglu (which might have been altered by previous plugins)""",
        },
    }
    
    
    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.cassandra_session = None
        self.cass_prep_quarantine = None
    
    
    def get_cassandra_session(self):
        if self.cassandra_session is None:
            keyspace=self.config.get(self.section,'cassandra_keyspace')
            # default idle_heartbeat_interval=30, we lower it to reduce write errors
            hosts = self.config.getlist(self.section,'cassandra_hosts')
            lbp = RoundRobinPolicy()
            cassandra_cluster = Cluster(hosts, protocol_version=4, idle_heartbeat_interval=10, load_balancing_policy=lbp)
            self.cassandra_session = cassandra_cluster.connect(keyspace)
            
            self.cass_prep_quarantine = self.cassandra_session.prepare("INSERT INTO quarantine (fugluid, messagecontent) VALUES (?, ?)  USING TTL ?")
        return self.cassandra_session
    
    
    def _cassandra_store(self, suspect, fugluid_override, retry=3):
        """Store message source into cassandra"""
        ttl=self.config.getint(self.section,'cassandra_ttl')
        original = self.config.getboolean(self.section, 'cassandra_useoriginal')
        content = self._get_msg_source(suspect, original)
        try:
            session = self.get_cassandra_session()
            fugluid = fugluid_override or suspect.id
            session.execute(self.cass_prep_quarantine, (fugluid, bytearray(content), ttl), timeout=20)
        except Exception as e:
            if retry>0:
                self.logger.info('%s failed to write to cassandra. try %s/3. error was: %s' % (suspect.id, retry, str(e)))
                time.sleep(0.1)
                self._cassandra_store(suspect, fugluid_override, retry-1)
            else:
                raise
    
    
    def archive(self, suspect, fugluid_override=None):
        result = {}
        self._cassandra_store(suspect, fugluid_override)
        self.logger.info('%s stored in cassandra' % suspect.id)
        result['success'] = True
        return result
        
        
    def lint(self):
        if not HAVE_CASSANDRA:
            print('ERROR: cassandra driver not available')
            return False
        
        import cassandra
        print("INFO: Cassandra Driver Version: %s" % cassandra.__version__)
        
        try:
            self.get_cassandra_session().execute("SELECT * FROM quarantine WHERE fugluid='dummy'")
        except Exception as e:
            print("ERROR: cassandra connection failed: %s"%str(e))
            return False
        
        return True



dovecot_username_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890.-_@'

def dovecot_username(username):
    legal_username = ''
    for char in username:
        if char in dovecot_username_chars:
            legal_username += char
    return legal_username


class MyLMTP(smtplib.LMTP):
    LMTP_PORT = 24
    
    # versions before 3.9 don't pass timeout to SMTP
    # https://github.com/python/cpython/blob/3.9/Lib/smtplib.py#L1079
    def __init__(self, host='', port=LMTP_PORT, local_hostname=None, source_address=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Initialize a new instance."""
        #super().__init__(host, port, local_hostname=local_hostname, source_address=source_address)
        smtplib.SMTP.__init__(self, host, port, local_hostname=local_hostname, source_address=source_address, timeout=timeout)
    
    
    
    # https://github.com/python/cpython/blob/3.9/Lib/smtplib.py#L803
    def sendmail(self, from_addr, to_addrs, msg, mail_options=(), rcpt_options=()):
        self.ehlo_or_helo_if_needed()
        esmtp_opts = []
        if isinstance(msg, str):
            # noinspection PyProtectedMember
            msg = smtplib._fix_eols(msg).encode('ascii')
        if self.does_esmtp:
            if self.has_extn('size'):
                esmtp_opts.append('size=%d' % len(msg))
            for option in mail_options:
                esmtp_opts.append(option)
        (code, resp) = self.mail(from_addr, esmtp_opts)
        if code != 250:
            if code == 421:
                self.close()
            else:
                self._rset()
            raise smtplib.SMTPSenderRefused(code, resp, from_addr)
        senderrs = {}
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]
        for each in to_addrs:
            (code, resp) = self.rcpt(each, rcpt_options)
            if (code != 250) and (code != 251):
                senderrs[each] = (code, resp)
            if code == 421:
                self.close()
                raise smtplib.SMTPRecipientsRefused(senderrs)
        if len(senderrs) == len(to_addrs):
            # the server refused all our recipients
            self._rset()
            raise smtplib.SMTPRecipientsRefused(senderrs)
        (code, resp) = self.data(msg)
        if code != 250:
            if code == 421:
                self.close()
            else:
                self._rset()
            raise smtplib.SMTPDataError(code, resp)
        # if we got here then somebody got our mail
        return senderrs, resp



class LMTPBackend(AbstractBackend):
    """
    This backend passes mail via LMTP to any LMTP server (however, only tested with dovecot)
    Status: Mature
    """
    requiredvars = {
        'lmtp_hosts': {
            'default': '',
            'description': 'comma separated list of LMTP target hostname, hostname:port or path to local LMTP socket (path must start with /)',
        },
        'lmtp_user': {
            'default': '',
            'description': 'LMTP auth user. leave empty if no authentication is needed',
        },
        'lmtp_password': {
            'default': '',
            'description': 'LMTP auth password. leave empty if no authentication is needed',
        },
        'lmtp_sender': {
            'default': '',
            'description': 'LMTP envelope sender. Leave empty for original SMTP envelope sender',
        },
        'lmtp_useoriginal': {
            'default': 'True',
            'description': """should we store the original message as retreived from postfix or store the
                                current state in fuglu (which might have been altered by previous plugins)""",
        },
        'lmtp_headername': {
            'default': 'X-Fuglu-ID',
            'description': 'Name of header containing Fuglu ID when storing via LMTP',
        },
    }


    def _parse_host_port(self, hostdefinition, defaultport=None):
        port = defaultport
        if ':' in hostdefinition:
            host, portstr = hostdefinition.split(':', 1)
            try:
                port = int(portstr)
            except ValueError:
                self.logger.warning(f'port {portstr} found in {hostdefinition} is not a number')
        else:
            host = hostdefinition
        return host, port
    
    
    def __init_socket(self):
        lmtp_hosts = self.config.getlist(self.section, 'lmtp_hosts')
        
        s = None
        if not lmtp_hosts:
            return None
        elif lmtp_hosts[0].startswith('/'):  # unix socket
            if not os.path.exists(lmtp_hosts[0]):
                raise Exception('unix socket %s not found' % lmtp_hosts)
            s = MyLMTP(lmtp_hosts)
        else:
            hosttuples = [self._parse_host_port(h, defaultport=MyLMTP.LMTP_PORT) for h in lmtp_hosts]
            for host, port in hosttuples:
                try:
                    s = MyLMTP(host, port, timeout=30)
                except (socket.error, ConnectionRefusedError):
                    continue
            if s is None and hosttuples:
                raise Exception('no LMTP server is reachable')
        return s
    
    
    def __auth(self, lmtp):
        user = self.config.get(self.section, 'lmtp_user')
        password = self.config.get(self.section, 'lmtp_password')
        if user and password:
            lmtp.login(user, password)
    
    
    def __do_quarantine(self, suspect, content, retry=3):
        host = 'unknown'
        lmtp_id = None
        
        lmtpfrom = self.config.get(self.section, 'lmtp_sender')
        if not lmtpfrom:
            lmtpfrom = suspect.from_address
        
        try:
            lmtp = self.__init_socket()
            # noinspection PyProtectedMember
            host = lmtp._host
            # make sure everything is correctly formatted to use sendmail
            # sendmail_address will make sure address type is correct for Py2/3, unicode/str/bytes
            # force_bString is bytes because we don't want the internal algorithm to play with
            # the message and try to encode it...
            rcpt = dovecot_username(suspect.to_address)
            senderrs, resp = lmtp.sendmail(force_uString(lmtpfrom), force_uString(rcpt), force_bString(content))
            lmtp.quit()
            if rcpt in senderrs:
                raise Exception('%s LMTP delivery error to %s on %s' % (suspect.id, rcpt, host))
            else:
                lmtp_id = self._lmtp_queueid(resp)
                self.logger.info('%s message delivered to LMTP server %s with LMTP ID %s' % (suspect.id, host, lmtp_id))
        except Exception as e:
            if retry > 0:
                self.logger.debug(
                    '%s LMTP delivery failed. try %s/3 on %s. error was: %s' % (suspect.id, retry, host, str(e)))
                time.sleep(0.1)
                self.__do_quarantine(suspect, content, retry - 1)
            else:
                raise
        
        return host, lmtp_id
    
    
    def _lmtp_queueid(self, resp):
        """
        sample response:
        '2.0.0 <rcpt@example.com> xIZNJoF4p1pDoAAALbRGFw Saved'

        #search msg in imap with this queue id or a message id:
        i = IMAP4('127.0.0.1')
        i.login('username', 'password')
        i.select()
        code, ids = i.uid('search', None, '(HEADER Received 'xIZNJoF4p1pDoAAALbRGFw')') # code is 'OK' if it was sucessful
        code, ids = i.search(None, '(HEADER Received 'xIZNJoF4p1pDoAAALbRGFw')')
        code, ids = i.search(None, '(HEADER Message-ID 'msgid@example.com')')
        code, ids = i.search(None, '(HEADER X-Fuglu-ID '09c68b914d66457508f6ad727d860d5b')')
        code, result = i.fetch(ids, '(RFC822)') # ids must be a set() or a string containing the id
        msgcontent = result[0][1]
        """
        if resp is None:
            return None
        qid = None
        resp = force_uString(resp)
        v = resp.split()
        if len(v) > 3:
            qid = v[2]
        return qid
    
    
    def archive(self, suspect, fugluid_override=None):
        original = self.config.getboolean(self.section, 'lmtp_useoriginal')
        content = self._get_msg_source(suspect, original)
        headername = self.config.get(self.section, 'lmtp_headername')
        if headername:
            fugluid = fugluid_override or suspect.id
            content = Suspect.prepend_header_to_source(headername, fugluid, force_bString(content))
        host, lmtp_id = self.__do_quarantine(suspect, content)
        return dict(host=host, lmtp_id=lmtp_id)
    
    
    def lint(self):
        if not self.config.get(self.section, 'lmtp_hosts'):
            print('WARNING: LMTP quarantine disabled')
            return True
        
        try:
            lmtp = self.__init_socket()
            if lmtp is None:
                print('ERROR: no LMTP connection defined')
                return False
            helo = lmtp.docmd('LHLO', get_outgoing_helo(self.config))
            helostr = helo[1].decode('utf-8')
            print('LMTP server sez: %s %s' % (helo[0], helostr))
            self.__auth(lmtp)
            lmtp.quit()
            success = True
        except Exception as e:
            print('ERROR: LMTP connection error: %s' % str(e))
            success = False
        
        return success



ARCHIVE_BACKENDS = OrderedDict()
ARCHIVE_BACKENDS['localdir'] = LocalDirBackend
ARCHIVE_BACKENDS['lmtp'] = LMTPBackend
ARCHIVE_BACKENDS['elastic'] = ElasticBackend
ARCHIVE_BACKENDS['cassandra'] = CassandraBackend


class ArchivePlugin(ScannerPlugin):

    """This plugins stores a copy of the message if it matches certain criteria (Suspect Filter). 
You can use this if you want message archives for your domains, need a quarantine or to debug problems occuring only for certain recipients.
The architecture allows to store data in various backends (databases), either simultaneously or using one backend as main and others as fallback in case the main backend is unavailable.
Currently the following backends are supported:
- localdir: save mail to a local directory structure. This backend is stable and in active use.
- lmtp: pass message to LMTP server. This backend is stable and in active use.
- elastic: store message in elasticsearch. This backend is in development (2021).
- cassandra: store message in cassandra. This backend is no longer maintained and published mainly for code archival reasons. YMMV.

Examples for the archive.regex filter file:

Archive messages to domain ''test.com'':

``to_domain test\.com``


Archive messages from oli@fuglu.org:


``envelope_from oli@fuglu\.org``


you can also append "yes" and "no" to the rules to create a more advanced configuration. Lets say we want to archive all messages to sales@fuglu.org and all regular messages support@fuglu.org except the ones created by automated scripts like logwatch or daily backup messages etc.

```
envelope_from logwatch@.*fuglu\.org   no
envelope_to sales@fuglu\.org yes
from backups@fuglu\.org no
envelope_to support@fuglu\.org      yes
```

Archive/Quarantine messages that are marked as spam:
```
@spam['spamassassin'] True
@archive.spam True
```

Note: The first rule to match in a message is the only rule that will be applied. Exclusion rules should therefore be put above generic/catch-all rules.
"""

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)

        self.requiredvars = {
            'archiverules': {
                'default': '${confdir}/archive.regex',
                'description': 'Archiving SuspectFilter File',
            },
            'archivebackends': {
                'default': 'localdir',
                'description': 'comma separated list of backends to use. available backends: %s' % ', '.join(list(ARCHIVE_BACKENDS.keys()))
            },
            'multibackend': {
                'default': 'False',
                'description': 'set to True to store mail in all enabled backends. set to False to only use primary and fallback to other backends on error'
            },
            'fugluid_headername': {
                'default': '',
                'description': 'Name of header containing alternative Fuglu ID that overrides storage key',
            },
            'fugluid_headername_skipmissing': {
                'default': 'True',
                'description': 'skip archiving if fugluid_headername is not set',
            },
            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },
        }
        for backend_name in ARCHIVE_BACKENDS:
            self.requiredvars.update(ARCHIVE_BACKENDS[backend_name].requiredvars)

        self.filter = None
        self.logger = self._logger()
        self.backends = OrderedDict()
    
    
    def __str__(self):
        return "Archive"
    
    
    def _load_backends(self):
        self.backends = OrderedDict()
        backend_names = self.config.getlist(self.section, 'archivebackends')
        for backend_name in backend_names:
            try:
                backendclass = ARCHIVE_BACKENDS[backend_name]
                backend = backendclass(self.config, self.section)
                self.backends[backend_name] = backend
            except KeyError:
                self.logger.error(f'invalid backend name {backend_name}')
    
    
    def do_archive(self, suspect):
        result = {}
        errors = {}
        
        headername = self.config.get(self.section, 'fugluid_headername')
        if not headername:
            fugluid_override = None
        else:
            fugluid_override = suspect.get_message_rep().get(headername)
            skipmissing = self.config.getboolean(self.section, 'fugluid_headername_skipmissing')
            if not fugluid_override and skipmissing:
                errors['preparation'] = 'could not find previous fugluid'
                return result, errors
            elif suspect.check_id(fugluid_override):
                errors['preparation'] = 'previous fugluid is not an md5 hash: %s' % fugluid_override
                return result, errors
        
        self._load_backends()
        multibackend = self.config.getboolean(self.section, 'multibackend')
        
        for backend_name in self.backends:
            backend = self.backends[backend_name]
            try:
                r = backend.archive(suspect, fugluid_override)
                result[backend_name] = r
                if not multibackend:
                    break
            except Exception as e:
                self.logger.error('failed to archive using backend %s due to %s' % (str(backend), str(e)))
                errors[backend_name] = str(e)
        return result, errors
    
    
    def _set_archive_tags(self, suspect):
        suspect.set_tag('archive.ham', suspect.is_ham())
        suspect.set_tag('archive.spam', suspect.is_spam())
        suspect.set_tag('archive.blocked', suspect.is_blocked())
        suspect.set_tag('archive.virus', suspect.is_virus())
    
    
    def _archive(self, suspect):
        suspect.set_tag('archived', False)
        archiverules = self.config.get(self.section, 'archiverules')
        if archiverules is None or archiverules == "":
            return DUNNO

        if not os.path.exists(archiverules):
            self.logger.error('%s Archive Rules file does not exist: %s' % (suspect.id, archiverules))
            return DUNNO

        if self.filter is None:
            self.filter = SuspectFilter(archiverules)
        
        self._set_archive_tags(suspect)
        match, arg = self.filter.matches(suspect)
        if match:
            if arg is not None and arg.lower().strip() == 'no':
                suspect.debug("Suspect matches archive exception rule")
                self.logger.debug("%s Header matches archive exception rule - not archiving" % suspect.id)
            else:
                if arg is not None and arg.lower().strip() != 'yes':
                    self.logger.warning("%s Unknown archive action '%s' assuming 'yes'" % (suspect.id, arg))
                self.logger.debug("%s Header matches archive rule" % suspect.id)
                if suspect.get_tag('debug'):
                    suspect.debug("Suspect matches archiving rule (would be archived it if we weren't in debug mode)" % suspect.id)
                else:
                    result, errors = self.do_archive(suspect)
                    if result:
                        suspect.set_tag('archived', True)
                    if errors:
                        self.logger.error('%s archiving errors in backend %s' % (suspect.id, ','.join(list(errors.keys()))))
                    suspect.set_tag('archived.result', result)
                    suspect.set_tag('archived.errors', errors)
                    
        else:
            suspect.debug("No archive rule/exception rule applies to this message")
            self.logger.debug("%s No archive rule/exception rule applies to this message" % suspect.id)
    
    
    def examine(self, suspect):
        self._archive(suspect)
        if not suspect.get_tag('archived') and suspect.get_tag('archived.errors'):
            return self._problemcode()
        return DUNNO
    
    
    def process(self, suspect, decision):
        self._archive(suspect)


    def lint_filter(self):
        filterfile = self.config.get(self.section, 'archiverules')
        sfilter = SuspectFilter(filterfile)
        return sfilter.lint()
    
    
    def lint(self):
        ok = self.check_config()
        if ok:
            ok = self.lint_filter()
        if ok:
            self._load_backends()
            for backend_name in self.backends:
                backend = self.backends[backend_name]
                backend_ok = backend.lint()
                if not backend_ok:
                    ok = False
        return ok