# -*- coding: UTF-8 -*-
import re
import os
from fuglu.shared import ScannerPlugin, AppenderPlugin, DUNNO, Suspect, FileList, get_outgoing_helo
from fuglu.stringencode import force_uString, force_bString
from fuglu.extensions.redisext import RedisPooledConn, redis, ENABLED as REDIS_AVAILABLE, ExpiringCounter
try:
    from domainmagic.util import unconfuse
    DOMAINMAGIC_AVAILABLE=True
except ImportError:
    DOMAINMAGIC_AVAILABLE=False
    def unconfuse(value):
        return value
try:
    import kafka
    KAFKA_AVAILABLE=True
except ImportError:
    KAFKA_AVAILABLE=False
    
    
    
class KnownSubjectMixin(object):
    config = None
    section = None
    requiredvars = {
        'redis_conn': {
            'default': '',
            'description': 'redis backend database connection: redis://host:port/dbid',
        },
        'headername': {
            'default': 'X-KnownSubjectScore',
            'description': 'header name',
        },
        'ttl': {
            'default': str(14 * 24 * 3600),
            'description': 'TTL in seconds',
        },
        'timeout': {
            'default': '2',
            'description': 'redis/kafka timeout in seconds'
        },
        'pinginterval': {
            'default': '0',
            'description': 'ping redis interval to prevent disconnect (0: don\'t ping)'
        },
        'skiplist': {
            'default': '${confdir}/knownsubject_skiplist.txt',
            'description': 'path to skiplist file, contains one skippable subject per line'
        },
        'kafkahosts': {
            'default': '',
            'description:': 'kafka bootstrap hosts: host1:port host2:port'
        },
        'kafkatopic': {
            'default': 'knownsubject',
            'description': 'name of kafka topic'
        },
        'kafkausername': {
            'default': '',
            'description:': 'kafka sasl user name for this producer'
        },
        'kafkapassword': {
            'default': '',
            'description': 'kafka sals password for this producer'
        },
    }



    def __init__(self):
        self.backend_redis=None
        self.backend_kafka = None
        self.skiplist = None
    
    
    
    def _init_skiplist(self):
        if self.skiplist is None:
            filepath = self.config.get(self.section, 'skiplist')
            if filepath and os.path.exists(filepath):
                self.skiplist = FileList(filename=filepath, additional_filters=[self._normalise_subject])
    
    
    
    def _init_backend_redis(self):
        """
        Init Redis backend if not yet setup.
        """
        if self.backend_redis is not None:
            return
        redis_conn = self.config.get(self.section, 'redis_conn')
        if redis_conn and REDIS_AVAILABLE:
            ttl = self.config.getint(self.section, 'ttl')
            socket_timeout = self.config.getint(self.section, 'timeout'),
            pinginterval = self.config.getint(self.section, 'pinginterval')
            redis_pool = RedisPooledConn(redis_conn, socket_keepalive=True, socket_timeout=socket_timeout, pinginterval=pinginterval)
            self.backend_redis = ExpiringCounter(redis_pool, ttl)
    
    
    def _insert_redis(self, suspect, subject):
        self._init_backend_redis()
        if self.backend_redis:
            multiplicator = self.config.getint(self.section, 'multiplicator')
            try:
                self.backend_redis.increase(subject, multiplicator)
                self.logger.info('%s subject %s registered in redis' % (suspect.id, subject))
            except redis.exceptions.TimeoutError as e:
                self.logger.error('%s failed to register subject in redis %s due to %s' % (suspect.id, subject, str(e)))
    
    
    def _init_backend_kafka(self):
        if self.backend_kafka is not None:
            return
        bootstrap_servers = self.config.getlist(self.section, 'kafkahosts')
        if bootstrap_servers and KAFKA_AVAILABLE:
            self.kafkatopic = self.config.get(self.section, 'kafkatopic')
            timeout = self.config.getint(self.section, 'timeout')
            username = self.config.get(self.section, 'kafkausername')
            password = self.config.get(self.section, 'kafkapassword')
            clientid = 'prod-fuglu-%s-%s' % (self.__class__.__name__, get_outgoing_helo(self.config))
            self.backend_kafka = kafka.KafkaProducer(bootstrap_servers=bootstrap_servers, api_version=(0, 10, 1), client_id=clientid,
                                                     request_timeout_ms=timeout*1000, sasl_plain_username=username, sasl_plain_password=password)
    
    
    def _insert_kafka(self, suspect, subject):
        if self.backend_kafka is None:
            self._init_backend_kafka()
        if self.backend_kafka:
            messagebytes = force_bString(subject)
            try:
                self.backend_kafka.send(self.kafkatopic, value=messagebytes, key=messagebytes)
                self.logger.info('%s subject %s registered in kafka' % (suspect.id, subject))
            except Exception as e:
                self.logger.error('%s failed to send message %s: %s' % (suspect.id, subject, str(e)))
                self.producer = None
        
    
    def _normalise_subject(self, subject, to_addr=None):
        s = Suspect.decode_msg_header(subject)
        s = force_uString(s)
        s = s.lower() # small caps only
        s = unconfuse(s) # replace all non-ascii characters by their ascii lookalike
        
        if to_addr:
            to_addr = force_uString(to_addr.lower())
            to_addr_lhs, to_addr_dom = to_addr.split('@',1)
            repl_map = [
                (to_addr, 'E'),
                (to_addr_lhs, 'L'),
                (to_addr_dom, 'D'),
            ]
            if '.' in to_addr_lhs:
                # maybe handle cases with more than one . in lhs
                fn, ln = to_addr_lhs.split('.',1)
                repl_map.append((fn, 'F'))
                repl_map.append((ln, 'S'))
            for k, v in repl_map: # remove to_addr,  to_addr lhs and domain name from subject
                s = s.replace(k, v)

        s = re.sub('^((?:re|fwd?|aw|tr|sv)\W?:?\s?)+', '',  s) # strip re/fwd prefix
        s = re.sub("(?:^|\s|\b|\w)([0-9'.,-]{2,16})(?:\s|\b|\w|$)", 'N', s) # replace all number groups
        s = re.sub('[0-9]', 'X', s) # replace individual numbers
        s = re.sub('\W', '', s, re.UNICODE) # remove all whitespaces and punctuations
        s = re.sub('[^\x00-\x7F]','U', s) # replace non-ascii chars (note: unconfuse has already replaced special
                                           #                               chars we care by an ascii representation
        s = s[:32] # shorten to a maximum of 32 chars
        return s
    
    
    def _get_subject(self, suspect):
        msgrep = suspect.get_message_rep()
        subject = suspect.decode_msg_header(msgrep.get('subject', ''))
        if not subject:
            return ''
        subject = self._normalise_subject(subject, suspect.to_address)
        if subject.isupper(): # ignore subjects that only consist of placeholders
            return ''
        if len(subject)<3: # ignore too short subjects
            return ''
        self._init_skiplist()
        if self.skiplist and subject in self.skiplist.get_list():
            return ''
        return subject
    
    
    def _lint_redis(self, fc):
        ok = True
        try:
            self._init_backend_redis()
            if self.backend_redis.redis_pool.check_connection():
                print(fc.strcolor("OK: ", "green"), "redis server replied to ping")
            else:
                ok = False
                print(fc.strcolor("ERROR: ", "red"), "redis server did not reply to ping")
    
        except redis.exceptions.ConnectionError as e:
            ok = False
            print(fc.strcolor("ERROR: ", "red"), f"failed to talk to redis server: {str(e)}")
        except Exception as e:
            ok = False
            print(fc.strcolor("ERROR: ", "red"), f" -> {str(e)}")
            import traceback
            traceback.print_exc()
        return ok
    
    
    def _lint_kafka(self, fc):
        ok = True
        try:
            self._init_backend_kafka()
        except kafka.errors.KafkaError as e:
            print('ERROR: failed to connect to kafka: %s' % str(e))
            ok = False
        except Exception as e:
            print('ERROR: Error connecting to kafka: %s' % str(e))
            self.logger.exception(e)
            ok = False
        return ok
    
    
    def lint(self):
        from fuglu.funkyconsole import FunkyConsole
        fc = FunkyConsole()
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            print(fc.strcolor("ERROR: ", "red"), 'neither redis nor kafka python module not available - this plugin will do nothing')
            return False
        
        ok = self.check_config()
        if ok:
            self._init_skiplist()
            if self.skiplist is None:
                print(fc.strcolor("WARNING: ", "red"), "skiplist not initialised")
                ok = False
        
        redis_conn = self.config.get(self.section, 'redis_conn')
        kafkahosts = self.config.get(self.section, 'kafkahosts')
        if not redis_conn and not kafkahosts:
            print(fc.strcolor("WARNING: ", "red"), "neither redis nor kafka specified, this plugin will have no effect")
        
        if ok:
            if redis_conn:
                ok = self._lint_redis(fc)
        
        if ok:
            if kafkahosts:
                ok = self._lint_kafka(fc)
        
        return ok



class KnownSubject(ScannerPlugin, KnownSubjectMixin):
    
    def __init__(self,config,section=None):
        ScannerPlugin.__init__(self,config,section)
        KnownSubjectMixin.__init__(self)
        self.logger = self._logger()
        
    
    
    def examine(self,suspect):
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            return DUNNO
        
        if not suspect.from_address:
            self.logger.debug('%s skipping bounce message' % suspect.id)
            return DUNNO
        
        suspect.set_tag('KnownSubjectRun', True)
        
        subject = self._get_subject(suspect)
        if not subject:
            self.logger.debug('%s skipping empty normalised subject' % suspect.id)
            return DUNNO
        
        suspect.set_tag('KnownSubject', subject)

        attempts = 2
        while attempts:
            attempts -= 1
            try:
                self._init_backend_redis()
                if self.backend_redis is None:
                    continue
                count = self.backend_redis.get_count(subject)
            except redis.exceptions.TimeoutError as e:
                self.logger.error(f'{suspect.id} failed to register subject {subject} due to {str(e)}')
                attempts = 0
            except redis.exceptions.ConnectionError as e:
                msg = f'{suspect.id} (retry={bool(attempts)}) failed to register subject {subject} due to {str(e)}'
                if attempts:
                    self.logger.warning(msg)
                    self.backend_redis = None
                else:
                    self.logger.error(msg)
            else:
                if count is not None and count > 0:
                    suspect.set_tag('KnownSubjectScore', count)
                    headername = self.config.get(self.section, 'headername')
                    suspect.write_sa_temp_header(headername, count)
                    self.logger.info('%s subject %s seen %s times' % (suspect.id, subject, count))
                else:
                    self.logger.debug('%s subject %s seen %s times' % (suspect.id, subject, 0))
                attempts = 0
        
        return DUNNO
    
    
    def lint(self):
        return KnownSubjectMixin.lint(self)
    
    
    
class KnownSubjectAppender(AppenderPlugin, KnownSubjectMixin):
    
    def __init__(self,config,section=None):
        AppenderPlugin.__init__(self,config,section)
        KnownSubjectMixin.__init__(self)
        self.logger = self._logger()

        self.requiredvars = KnownSubjectMixin.requiredvars
        requiredvars={
            'multiplicator': {
                'default': '1',
                'description': 'how many times does each entry count. you may want to set a higher value for trap processors'
            },
            'reportall': {
                'default': '0',
                'description': 'True: report all mails. False: only report spam/virus'
            },
        }
        self.requiredvars.update(requiredvars)
    
    
    
    def process(self, suspect, decision):
        if not REDIS_AVAILABLE and not KAFKA_AVAILABLE:
            return
        
        if not suspect.from_address:
            self.logger.debug('%s skipping bounce message' % suspect.id)
            return
        
        reportall = self.config.getboolean(self.section, 'reportall')
        if not reportall and not (suspect.is_spam() or suspect.is_virus()):
            self.logger.debug('%s skipped: not spam or virus' % suspect.id)
            return
        
        has_run = suspect.get_tag('KnownSubjectRun', False)
        if has_run:
            subject = suspect.get_tag('KnownSubject')
        else:
            subject = self._get_subject(suspect)
            if not subject:
                self.logger.debug('%s skipping empty normalised subject' % suspect.id)
                return
            
        if subject is not None:
            self._insert_redis(suspect, subject)
            self._insert_kafka(suspect, subject)
            
        return
    
    
    def lint(self):
        return KnownSubjectMixin.lint(self)
    
    
    
    
    
