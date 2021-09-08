# -*- coding: utf-8 -*-
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

import logging
import socket
import tempfile
import os
import typing as tp
import asyncio
import traceback
import time
import datetime
import functools
import copy

from email.header import Header
from io import BytesIO

from fuglu.protocolbase import ProtocolHandler
from fuglu.stringencode import force_bString, force_uString
from fuglu.shared import Suspect, DUNNO, REJECT, DELETE, DEFER, ACCEPT, string_to_actioncode
from fuglu.scansession import TrackTimings
from configparser import ConfigParser
from fuglu.logtools import createPIDinfo
from fuglu.debug import CrashStore
from fuglu.addrcheck import Addrcheck

try:
    import libmilter as lm
    import fuglu.lib.patchedlibmilter as lmp

    # ## overwrite debug logger if required
    # def debug(msg, level=1, protId=0):
    #     out = ''
    #     if protId:
    #         out += f'ID: {protId} ; '
    #     out += msg
    #     logging.getLogger("libmilter").debug(out)
    # lm.debug = debug

    LIMBMILTER_AVAILABLE = True
except ImportError:
    class lm:
        MilterProtocol = object
        SMFIF_ALLOPTS = None

        ACCEPT = b"accept"
        CONTINUE = b"continue"
        REJECT = b"reject"
        TEMPFAIL = b"tempfail"
        DISCARD = b"discard"
        CONN_FAIL = b"conn_fail"
        SHUTDOWN = b"shutdown"

        @staticmethod
        def noReply(self):
            pass

    class lmp(lm):
        ASYNCMilterProtocol = object

    LIMBMILTER_AVAILABLE = False


# string to return code
STR2RETCODE = {
    "accept": lm.ACCEPT,
    "continue": lm.CONTINUE,
    "reject": lm.REJECT,
    "tempfail": lm.TEMPFAIL,
    "discard": lm.DISCARD,
    "conn_fail": lm.CONN_FAIL,
    "shutdown": lm.SHUTDOWN
}


RETCODE2STR = dict([(v, k) for k,v in STR2RETCODE.items()])


# states
CONNECT = "connect"
HELO = "helo"
MAILFROM = "mailfrom"
RCPT = "rcpt"
HEADER = "header"
EOH = "eoh"
EOB = "eob"

BE_VERBOSE = False

class MilterHandler(TrackTimings):
    protoname = 'MILTER V6'
    def __init__(self, config, prependers: tp.List,
                 plugins: tp.List, appenders: tp.List, port: int,
                 milterplugins: tp.Dict, workerstate=None, asyncid=None, enable=False,
                 pool=None):

        TrackTimings.__init__(self, enable=enable, port=port)
        self.config = config
        self.logger = logging.getLogger('fuglu.%s' % self.__class__.__name__)
        self.prependers = prependers
        self.plugins = plugins
        self.appenders = appenders
        self.milterplugins = milterplugins
        self.port = port
        self.action = DUNNO
        self.message = None
        self.be_verbose = BE_VERBOSE
        self.workerstate = workerstate
        self.asyncid = asyncid
        self.pool = pool

        try:
            self._att_mgr_cachesize = config.getint('performance', 'att_mgr_cachesize')
        except Exception:
            self._att_mgr_cachesize = None
        try:
            self._att_defaultlimit = self.config.getint('performance', 'att_mgr_default_maxextract')
        except Exception:
            self._att_defaultlimit = None
        try:
            self._att_maxlimit = self.config.getint('performance', 'att_mgr_hard_maxextract')
        except Exception:
            self._att_maxlimit = None

        # here sock should come in as a tuple with async stream (reader, writer)
        self.socket = None

        # Milter can keep the connection and handle several suspect in one session
        self.keep_connection = True

        if not LIMBMILTER_AVAILABLE:
            raise ImportError("libmilter not available, not possible to use MilterHandler")

        try:
            configstring = config.get('milter', 'milter_mode')
        except Exception:
            configstring = "tags"

        configstring = configstring.lower()

        if not configstring:
            self.log("milter_mode: setting to default value: 'tags'")
            configstring = "tags"

        if configstring not in ["auto", "readonly", "tags", "replace_demo", "manual"]:
            self.logger.warning("milter_mode: '%s' not recognised, resetting to 'tags'" % configstring)

        self.enable_mode_manual = ("manual" in configstring)
        self.enable_mode_auto = ("auto" in configstring)
        self.enable_mode_readonly = ("readonly" in configstring)
        self.enable_mode_tags = ("tags" in configstring)
        self.replace_demo = ("replace_demo" in configstring)

        self.sess_options = 0x00 if self.enable_mode_readonly else lm.SMFIF_ALLOPTS

        self.logger.debug(f"{createPIDinfo()}: new MilterHandler (asyncid: {asyncid})")
        self.log(f"Milter mode: auto={self.enable_mode_auto}, "
                 f"readonly={self.enable_mode_readonly}, "
                 f"tags={self.enable_mode_tags}")

        # options (can be combined into a string): "all" "body" "headers" "from" "to"
        try:
            self.milter_mode_options = config.get('milter', 'milter_mode_options')
        except Exception:
            self.milter_mode_options = ""

        self.log("Milter config fixed replacements: all=%s, body=%s, headers=%s, from=%s, to=%s" %
                 ("all" in self.milter_mode_options, "body" in self.milter_mode_options,
                  "headers" in self.milter_mode_options, "from" in self.milter_mode_options,
                  "to" in self.milter_mode_options))
        self.log(f"prependers: {self.prependers}")
        self.log(f"plugins: {self.plugins}")
        self.log(f"appenders: {self.appenders}")
        self.log(f"milterplugins: {self.milterplugins}")

    def resettimer(self):
        self.logger.debug("Resetting timer...")
        super().resettimer()

    def log(self, msg):
        # function will be used by libmilter as well for logging
        # this is only for development/debugging, that's why it has
        # to be enabled in the source code
        if self.be_verbose:
            self.logger.debug(msg)

    def set_workerstate(self, status):
        if self.workerstate is not None:
            if self.asyncid:
                self.workerstate.set_workerstate(status, id=self.asyncid)
            else:
                self.workerstate.workerstate = status

    def run_suspect_plugins(self, pluglist: tp.List, suspect: Suspect, message_prefix: str = "") -> tp.Tuple[int, tp.Optional[str]]:
        self.tracktime("Message-Receive-Suspect")

        # reset MilterHandler return actions in case there's a connection re-used
        self.action = DUNNO
        self.message = None

        if len(suspect.recipients) != 1:
            self.logger.warning(
                message_prefix + u'Notice: Message from %s has %s recipients. Plugins supporting only one recipient will see: %s' % (
                    suspect.from_address, len(suspect.recipients), suspect.to_address))
        self.logger.debug(message_prefix + u"Message from %s to %s: %s bytes stored to %s" % (
            suspect.from_address, suspect.to_address, suspect.size, suspect.tempfilename()))

        self.set_workerstate(message_prefix + u"Handling message %s" % suspect)
        # store incoming port to tag, could be used to disable plugins
        # based on port

        starttime = time.time()
        self.run_plugins(suspect, pluglist)

        prependheader = self.config.get('main', 'prependaddedheaders')
        # Set fuglu spam status if wanted
        if self.config.getboolean('main', 'spamstatusheader'):
            if suspect.is_spam():
                suspect.add_header("%sSpamstatus" % prependheader, 'YES')
            else:
                suspect.add_header("%sSpamstatus" % prependheader, 'NO')

        # how long did it all take?
        difftime = time.time() - starttime
        suspect.tags['fuglu.scantime'] = "%.4f" % difftime

        # Debug info to mail
        if self.config.getboolean('main', 'debuginfoheader'):
            debuginfo = str(suspect)
            suspect.add_header("%sDebuginfo" % prependheader, debuginfo)

        # add suspect id for tracking
        if self.config.getboolean('main', 'suspectidheader'):
            suspect.add_header('%sSuspect' % prependheader, suspect.id)
        self.tracktime("Adding-Headers")

        # checks done.. print out suspect status
        logformat = self.config.get('main', 'logtemplate')
        if logformat.strip() != '':
            self.logger.info(suspect.log_format(logformat))
        suspect.debug(suspect)
        self.tracktime("Debug-Suspect")

        # check if one of the plugins made a decision
        result = self.action

        self.set_workerstate(message_prefix + u"Finishing message %s" % suspect)

        return result, self.message

    def run_plugins(self, suspect, pluglist):
        """Run scannerplugins on suspect"""
        suspect.debug('Will run plugins: %s' % pluglist)
        self.tracktime("Before-Plugins")
        for plugin in pluglist:
            try:
                iscoroutine = asyncio.iscoroutinefunction(plugin.examine)
                msg = f"{suspect.id} Running(async={iscoroutine}) Plugin: {str(plugin)}"
                self.set_workerstate(msg)
                self.logger.debug(msg)

                starttime = time.time()

                # run plugin (async if possible)
                ans = plugin.run_examine(suspect)

                plugintime = time.time() - starttime
                suspect.tags['scantimes'].append((plugin.section, plugintime))
                message = None
                if type(ans) is tuple:
                    result, message = ans
                else:
                    result = ans

                if result is None:
                    result = DUNNO

                suspect.tags['decisions'].append((plugin.section, result))

                if result == DUNNO:
                    suspect.debug('Plugin makes no final decision')
                    self.logger.debug(f'{suspect.id} Plugin makes no final decision')
                elif result == ACCEPT:
                    suspect.debug('Plugin accepts the message - skipping all further tests')
                    self.logger.debug(f'{suspect.id} Plugin says: ACCEPT. Skipping all other tests')
                    self.action = ACCEPT
                    break
                elif result == DELETE:
                    suspect.debug('Plugin DELETES this message - no further tests')
                    self.logger.debug(f'{suspect.id} Plugin says: DELETE. Skipping all other tests')
                    self.action = DELETE
                    self.message = message
                    self.trash(suspect, str(plugin))
                    break
                elif result == REJECT:
                    suspect.debug('Plugin REJECTS this message - no further tests')
                    self.logger.debug(f'{suspect.id} Plugin says: REJECT. Skipping all other tests')
                    self.action = REJECT
                    self.message = message
                    break
                elif result == DEFER:
                    suspect.debug('Plugin DEFERS this message - no further tests')
                    self.logger.debug(f'{suspect.id} Plugin says: DEFER. Skipping all other tests')
                    self.action = DEFER
                    self.message = message
                    break
                else:
                    self.logger.error(f'{suspect.id} Invalid Message action Code: %s. Using DUNNO' % result)

            except Exception as e:
                CrashStore.store_exception()
                exc = traceback.format_exc()
                self.logger.error(f'{suspect.id}Plugin %s failed: %s' % (str(plugin), exc))
                suspect.debug('Plugin failed : %s . Please check fuglu log for more details' % e)
                ptag = suspect.get_tag("processingerrors", defaultvalue=[])
                ptag.append("Plugin %s failed: %s" % (str(plugin), str(e)))
                suspect.set_tag("processingerrors", ptag)
            finally:
                self.tracktime(str(plugin), plugin=True)

    def run_prependers(self, suspect):
        """Run prependers on suspect"""
        plugcopy = self.plugins[:]
        appcopy = self.appenders[:]

        self.tracktime("Before-Prependers")
        for plugin in self.prependers:
            try:
                self.logger.debug('Running prepender %s' % plugin)
                self.set_workerstate("%s : Running Prepender %s" % (suspect, plugin))
                starttime = time.time()

                out_plugins = plugin.pluginlist(suspect, plugcopy)
                out_appenders = plugin.appenderlist(suspect, appcopy)

                plugintime = time.time() - starttime
                suspect.tags['scantimes'].append((plugin.section, plugintime))

                # Plugins
                if out_plugins is not None:
                    plugcopyset = set(plugcopy)
                    resultset = set(out_plugins)
                    removed = list(plugcopyset - resultset)
                    added = list(resultset - plugcopyset)
                    if len(removed) > 0:
                        self.logger.debug(
                            'Prepender %s removed plugins: %s' % (plugin, list(map(str, removed))))
                    if len(added) > 0:
                        self.logger.debug(
                            'Prepender %s added plugins: %s' % (plugin, list(map(str, added))))
                    plugcopy = out_plugins

                # Appenders
                if out_appenders is not None:
                    appcopyset = set(appcopy)
                    resultset = set(out_appenders)
                    removed = list(appcopyset - resultset)
                    added = list(resultset - appcopyset)
                    if len(removed) > 0:
                        self.logger.debug(
                            'Prepender %s removed appender: %s' % (plugin, list(map(str, removed))))
                    if len(added) > 0:
                        self.logger.debug(
                            'Prepender %s added appender: %s' % (plugin, list(map(str, added))))
                    appcopy = out_appenders

            except Exception as e:
                CrashStore.store_exception()
                exc = traceback.format_exc()
                self.logger.error(
                    'Prepender plugin %s failed: %s' % (str(plugin), exc))
                ptag = suspect.get_tag("processingerrors", defaultvalue=[])
                ptag.append("Prepender %s failed: %s" % (str(plugin), str(e)))
                suspect.set_tag("processingerrors", ptag)
            finally:
                self.tracktime(str(plugin), prepender=True)
        return plugcopy, appcopy

    def run_appenders(self, suspect, finaldecision, applist):
        """Run appenders on suspect"""
        if suspect.get_tag('noappenders'):
            return

        self.tracktime("Before-Appenders")
        for plugin in applist:
            try:
                self.logger.debug('Running appender %s' % plugin)
                suspect.debug('Running appender %s' % plugin)
                self.set_workerstate("%s : Running appender %s" % (suspect, plugin))
                starttime = time.time()
                plugin.process(suspect, finaldecision)
                plugintime = time.time() - starttime
                suspect.tags['scantimes'].append((plugin.section, plugintime))
            except Exception as e:
                CrashStore.store_exception()
                exc = traceback.format_exc()
                self.logger.error(
                    'Appender plugin %s failed: %s' % (str(plugin), exc))
                ptag = suspect.get_tag("processingerrors", defaultvalue=[])
                ptag.append("Appender %s failed: %s" % (str(plugin), str(e)))
                suspect.set_tag("processingerrors", ptag)
            finally:
                self.tracktime(str(plugin), appender=True)

    def trash(self, suspect, killerplugin=None):
        """copy suspect to trash if this is enabled"""
        trashdir = self.config.get('main', 'trashdir').strip()
        if trashdir == "":
            return

        if not os.path.isdir(trashdir):
            try:
                os.makedirs(trashdir)
            except OSError:
                self.logger.error(
                    "Trashdir %s does not exist and could not be created" % trashdir)
                return
            self.logger.info('Created trashdir %s' % trashdir)

        trashfilename = ''
        try:
            handle, trashfilename = tempfile.mkstemp(
                prefix=suspect.id, dir=self.config.get('main', 'trashdir'))
            with os.fdopen(handle, 'w+b') as trashfile:
                trashfile.write(suspect.get_source())
            self.logger.debug('Message stored to trash: %s' % trashfilename)
        except Exception as e:
            self.logger.error(
                "could not create file %s: %s" % (trashfilename, e))

        # TODO: document main.trashlog
        if self.config.has_option('main', 'trashlog') and self.config.getboolean('main', 'trashlog'):
            try:
                with open('%s/00-fuglutrash.log' % self.config.get('main', 'trashdir'), 'a') as handle:
                    # <date> <time> <from address> <to address> <plugin that said "DELETE"> <filename>
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    handle.write("%s %s %s %s %s" % (
                        now, suspect.from_address, suspect.to_address, killerplugin, trashfilename))
                    handle.write("\n")
            except Exception as e:
                self.logger.error("Could not update trash log: %s" % e)


class MilterSession(lmp.ASYNCMilterProtocol):
    def __init__(self,
                 reader: tp.Optional[asyncio.StreamReader],
                 writer: tp.Optional[asyncio.StreamWriter],
                 config: tp.Optional[ConfigParser] = None,
                 options: bytes = lm.SMFIF_ALLOPTS,
                 mhandler: tp.Optional[MilterHandler] = None,
                 ):
        # additional parameters (suspect creation)
        self.mhandler = mhandler
        self.logger = logging.getLogger('fuglu.miltersession')

        # enable options for version 2 protocol
        super().__init__(reader=reader, writer=writer, opts=options)
        lm.MilterProtocol.__init__(self, opts=options)
        self.timestamp = time.time()

        self.asyncbuffer = []
        self.reader = reader
        self.writer = writer
        self.transport = self.writer.get_extra_info('socket')  # extract socket instance
                                                               # (atm only needed for port extraction)

        # a message counter for the session, similar
        # to what we have in fuglu.scansession.SessionHandler
        # -> counter is always increased when we reach eob
        self.imessage = 0


        try:
            self.tmpdir = config.get('main', 'tempdir')
        except Exception:
            self.tmpdir = "/tmp"

        try:
            self.async_read_timeout = config.getfloat('performance', 'async_read_timeout')
        except Exception:
            self.async_read_timeout = None

        try:
            self.async_recproc_timeout = config.getfloat('performance', 'async_recproc_timeout')
        except Exception:
            self.async_recproc_timeout = None

        try:
            self.async_conlost_timeout = config.getfloat('performance', 'async_conlost_timeout')
        except Exception:
            self.async_conlost_timeout = None

        self.be_verbose = BE_VERBOSE

        if self.be_verbose:
            self.logger.debug("Options negotiated:")
            for smfip_option, smfip_string in iter(lm.SMFIP_PROTOS.items()):
                self.logger.debug("* %s: %s" % (smfip_string, bool(smfip_option & self.protos)))

        # connection
        self.heloname = None
        self.addr = None
        self.fcrdns = None
        self.ptr = None

        self.recipients = []
        self.sender = None

        self._buffer = None
        self._tempfile = None
        self.tempfilename = None
        self.original_headers = []
        # postfix queue id
        self.queueid = None
        # SASL authentication
        self.sasl_login = None
        self.sasl_sender = None
        self.sasl_method = None
        # unique id
        self._id = None

        # connection encryption
        self.cipher = None
        self.cipher_bits = None
        self.cert_subject = None
        self.cert_issuer = None
        self.tls_version = None

        # headers to add to mail
        self.addheaders = {}

        # tags (will be passed to Suspect)
        self.tags = {}

        # tags backup to reset to connect
        self.tags_backup = {}

        self.logger.debug(f"{createPIDinfo()}: new MilterSession")

    @property
    def sasl_user(self):
        return self.sasl_login

    def add_header(self, key: str, value: str):
        """ Headers to add to mail (if allowed) """
        self.addheaders[key] = value

    def add_plugin_skip(self, pluginname: str, tag: str = "skipmplugins"):
        """Add plugin to skiplist"""
        if tag in self.tags:
            # append if already present
            self.tags[tag] = f"{self.tags[tag]},{pluginname}"
        else:
            # set tag
            self.tags[tag] = pluginname

    def skip_plugin(self, plugin, tag: str = "skipmplugins") -> bool:
        """Check if plugin is in skiplist"""
        from fuglu.mshared import BasicMilterPlugin
        plugin: tp.Union[str, BasicMilterPlugin]
        res = False
        try:
            skipstring = self.tags.get(tag)
            if isinstance(plugin, str):
                pluginname = plugin
            else:
                pluginname = plugin.__class__.__name__
            res = skipstring and pluginname in Suspect.getlist_space_comma_separated(skipstring)
        except Exception:
            pass
        return res

    async def _connect(self, cmd, data):
        """
        Wrap connect to be able to make a tags-backup. Required so tags set
        based on connect can be restored.
        """
        res = await super()._connect(cmd, data)
        # make a backup of the tags to be used for a reset
        self.tags_backup = copy.deepcopy(self.tags)
        return res

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val
        # whenever id is set, reset timings for MilterHandler
        if self.mhandler:
            self.mhandler.resettimer()

        self.logger.debug(f"{createPIDinfo()}: new MilterSession id: {val}")

    def get_templ_dict(self, setall: bool = False) -> tp.Dict[str, tp.Any]:
        templdict = {}
        if setall or self.id is not None:
            templdict['id'] = force_uString(self.id)
        if setall or self.heloname is not None:
            templdict['heloname'] = force_uString(self.heloname)
        if setall or self.fcrdns is not None:
            templdict['fcrdns'] = force_uString(self.fcrdns)
        if setall or self.ptr is not None:
            templdict['ptr'] = force_uString(self.ptr)
        if setall or self.addr is not None:
            templdict['addr'] = force_uString(self.addr)
        if setall or self.queueid is not None:
            templdict['queueid'] = force_uString(self.queueid)
        if setall or self.sasl_login is not None:
            templdict['sasl_login'] = force_uString(self.sasl_login)
        if setall or self.sasl_user is not None: # same as sasl_login
            templdict['sasl_user'] = force_uString(self.sasl_user)
        if setall or self.sasl_sender is not None:
            templdict['sasl_sender'] = force_uString(self.sasl_sender)
        if setall or self.from_address:
            templdict['from_address'] = self.from_address
        if setall or self.from_domain:
            templdict['from_domain'] = self.from_domain
        # latest recipient
        if setall or self.to_address:
            templdict['to_address'] = self.to_address
        if setall or self.to_domain:
            templdict['to_domain'] = self.to_domain
        if setall or self.size is not None:
            templdict['size'] = force_uString(self.size)
        if setall or self.cipher is not None:
            templdict['cipher'] = force_uString(self.cipher)
        if setall or self.cipher_bits is not None:
            templdict['cipher_bits'] = force_uString(self.cipher_bits)
        if setall or self.cert_subject is not None:
            templdict['cert_subject'] = force_uString(self.cert_subject)
        if setall or self.cert_issuer is not None:
            templdict['cert_issuer'] = force_uString(self.cert_issuer)
        if setall or self.tls_version is not None:
            templdict['tls_version'] = force_uString(self.tls_version)
        # put tags also in template dict with prefix "tag_" so it can be
        # used in reject messages
        if self.tags:
            for tkey, tval in self.tags.items():
                templdict[f'tag_{tkey}'] = f"{tval}"
        return templdict

    def reset_connection(self):
        """Reset all variables except to prepare for a second mail through the same connection.
        keep helo (heloname), ip address (addr) and hostname (fcrdns)"""
        if self.id and self.mhandler:
            self.mhandler.report_timings(suspectid=self.id, withrealtime=True)
        self.recipients = []
        self.original_headers = []
        self._buffer = None
        if self.tempfilename and os.path.exists(self.tempfilename):
            try:
                os.remove(self.tempfilename)
                self.logger.info("Abort -> removed temp file: %s" % self.tempfilename)
            except OSError:
                self.logger.error("Could not remove tmp file: %s" % self.tempfilename)
                pass
        self.tempfilename = None
        # postfix queue id
        self.queueid = None
        # SASL authentication
        self.sasl_login = None
        self.sasl_sender = None
        self.sasl_method = None
        self.action = DUNNO
        self.message = None
        self.addheaders = {}
        self.tags = copy.deepcopy(self.tags_backup)
        self.id = Suspect.generate_id()
        if self.mhandler:
            self.mhandler.resettimer()

    def _clean_address(self, address: tp.Optional[bytes]) -> tp.Optional[bytes]:
        address_cleaned = None
        # convert address to string
        if address is not None:
            addr_split = address.split(b'\0', maxsplit=1)
            address_cleaned = addr_split[0].strip(b'<>')
        return address_cleaned

    def get_cleaned_from_address(self) -> bytes:
        """Return from_address, without <> qualification or other MAIL FROM parameters"""
        # now already cleaned while setting
        return self.sender

    def get_cleaned_recipients(self) -> tp.List[bytes]:
        """Return recipient addresses, without <> qualification or other RCPT TO parameters"""
        # now already cleaned while setting
        return self.recipients


    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = BytesIO()
        return self._buffer

    @buffer.setter
    def buffer(self, value):
        if self._buffer:
            try:
                del self._buffer
            except Exception as e:
                self.logger.debug(f"{self.id} error setting buffer to {value}: {str(e)}")
        self._buffer = value

    @property
    def size(self):
        try:
            return self._buffer.getbuffer().nbytes
        except Exception:
            return 0

    @staticmethod
    def extract_domain(address: str, lowercase=True):
        if not address or address.lower() == "postmaster":
            return None
        else:
            try:
                user, domain = address.rsplit('@', 1)
                if lowercase:
                    domain = domain.lower()
                return domain
            except Exception as e:
                raise ValueError("invalid email address: '%s'" % address)

    @property
    def from_address(self):
        return force_uString(self.sender)

    @property
    def from_domain(self):
        from_address = self.from_address
        if from_address is None:
            return None
        try:
            return MilterSession.extract_domain(from_address)
        except ValueError:
            return None

    @property
    def to_address(self):
        if self.recipients:
            rec = force_uString(self.recipients[-1])
            return rec
        else:
            return None

    @property
    def to_domain(self):
        rec = self.to_address
        if rec is None:
            return None
        try:
            return MilterSession.extract_domain(rec)
        except ValueError:
            return None

    async def send_reply_message(self, rcode: int, xcode: str, msg: str):
        def_xcode = ""
        if int(rcode/100) == 5:
            def_xcode = "5.7.1"
        elif int(rcode/100) == 4:
            def_xcode = "4.7.1"

        if xcode:
            await self.sendReply(rcode, xcode, msg)
        elif def_xcode:
            if not msg.startswith(def_xcode[:2]):
                await self.sendReply(rcode, def_xcode, msg)
            else:
                split = msg.split(" ", 1)
                if len(split) == 2:
                    await self.sendReply(rcode, split[0], split[1])
                else:
                    await self.sendReply(rcode, "", msg)
        else:
            await self.sendReply(rcode, "", msg)

    async def sendReply(self, rcode: int, xcode: str, msg: str):
        # actually sendReply needs all bytes
        from fuglu.mshared import SumAsyncTime

        # include in async timing
        with SumAsyncTime(self.mhandler, "sendReply", logid=self.id):
            return await super().sendReply(force_bString(rcode), force_bString(xcode), force_bString(msg))

    @staticmethod
    def milter_return_code(incode: tp.Union[int, bytes]):
        outres = incode
        returncode = None
        if isinstance(incode, int):
            # integer returncode, not bytecode
            returncode = incode
            if 500 < returncode < 599:
                outres = lm.REJECT
            elif 400 < returncode < 499:
                outres = lm.TEMPFAIL
            elif 200 < returncode < 299:
                outres = lm.ACCEPT
            else:
                outres = lm.CONTINUE
        return outres, returncode

    async def handle_milter_plugin_reply(self,
                                         res: tp.Union[bytes, tp.Tuple[bytes, str], tp.Tuple[int, str]],
                                         fugluid: tp.Optional[str] = None):
        """Handle reply from plugin which might contain a message to set for the reply"""
        try:
            outres, message = res
            if message is None:
                message = ""

            # if outres is integer, create bytecode & integer-code, otherwise keep bytecode
            outres, returncode = MilterSession.milter_return_code(incode=outres)

            message = force_uString(message)
            if message and fugluid and fugluid not in message:
                # if fugluid is not in message -> append
                message = f"{message.rstrip()} ({fugluid})"
            elif not message:
                message = f"({fugluid})"

            if outres == lm.TEMPFAIL:
                await self.send_reply_message(returncode if returncode else 450, "", message)
                # Deferred which will not send anything back to the mta.
                # (send_reply_message already sent the response...)
                returncode = lm.Deferred()
            elif outres == lm.REJECT:
                await self.send_reply_message(returncode if returncode else 550, "", message)
                # Deferred which will not send anything back to the mta.
                # (send_reply_message already sent the response...)
                returncode = lm.Deferred()
        except ValueError:
            outres = res
            outres, returncode = MilterSession.milter_return_code(incode=outres)
            returncode = res
            message = ""
        except Exception as e:
            self.logger.error(f"handle_milter_plugin_reply exception: {str(e)}", exc_info=e)
            outres = res
            outres, returncode = MilterSession.milter_return_code(incode=outres)
            returncode = res
            message = ""

        if not message and fugluid:
            # if fugluid is not in message -> append
            message = f"({fugluid})"

        return outres, message, returncode

    def has_option(self, smfif_option, client=None):
        """
        Checks if option is available. Fuglu or mail transfer agent can
        be checked also separately.

        Args:
            smfif_option (int): SMFIF_* option as defined in libmilter
            client (str,unicode,None): which client to check ("fuglu","mta" or both)

        Returns:
            (bool): True if available

        """
        option_fuglu = True if smfif_option & self._opts else False
        option_mta = True if smfif_option & self._mtaOpts else False
        if client == "fuglu":
            return option_fuglu
        elif client == "mta":
            return option_mta
        else:
            return option_fuglu and option_mta

    async def handlesession(self) -> bool:
        """Get mail(s), process milter plugins, create & process suspect"""

        from fuglu.mshared import SumAsyncTime

        # already generate Suspect id
        # set in session already for logging
        # so we can link milter logs in different states to final suspect
        self.id = Suspect.generate_id()

        """Get incoming mail, process Milter plugins for each stage"""
        self._sockLock = lm.DummyLock()
        while True:
            buf = ''
            try:
                self.log("receive data from transport")
                reader: asyncio.StreamReader = self.reader
                with SumAsyncTime(self.mhandler, 'reader', logid=self.id):
                    if self.async_read_timeout:
                        buf = await asyncio.wait_for(reader.read(lm.MILTER_CHUNK_SIZE), timeout=self.async_read_timeout)
                    else:
                        buf = await reader.read(lm.MILTER_CHUNK_SIZE)
                self.log("after receive")
            except asyncio.TimeoutError as e:
                self.logger.error(f"{self.id} Async-Timeout(t={self.async_read_timeout}) waiting for data: {str(e)}")
            except (AttributeError, socket.error, socket.timeout) as e:
                # Socket has been closed, error or timeout happened
                self.log(f"receive error: {e}, buffer is: {buf}")
            if not buf:
                self.log("buf is empty -> return")
                return True
            elif self.be_verbose:
                self.log(f"buf is non-empty, len={len(buf)}")
            try:
                # dataReceived will process, so we don't want to
                # include it in async time
                if self.async_recproc_timeout:
                    await asyncio.wait_for(self.dataReceived(buf), timeout=self.async_recproc_timeout)
                else:
                    await self.dataReceived(buf)
                self.log(f"after dataReceived")
            except asyncio.TimeoutError as e:
                self.logger.error(f"{self.id} Async-Timeout(t={self.async_recproc_timeout}) dataReceived(processing): {str(e)}")
            except Exception as e:
                self.logger.error(f'{self.id} AN EXCEPTION OCCURED IN {self.id}: {str(e)}', exc_info=e)
                self.log("Call connectionLost")
                try:
                    if self.async_conlost_timeout:
                        await asyncio.wait_for(self.connectionLost(), timeout=self.async_conlost_timeout)
                    else:
                        await self.connectionLost()
                except asyncio.TimeoutError as e:
                    self.logger.error(f"{self.id} Async-Timeout(t={self.async_recproc_timeout}) connectionLost: {str(e)}")
                except Exception as e:
                    self.logger.error(f"{self.id} while connectionLost: {str(e)}")

                self.log("fail -> return false")
                return False

    def log(self, msg):
        # function will be used by libmilter as well for logging
        # this is only for development/debugging, that's why it has
        # to be enabled in the source code
        if self.be_verbose:
            self.logger.debug(msg)

    def store_info_from_dict(self, command_dict):
        """Extract and store additional info passed by dict"""
        if command_dict:
            if not self.queueid:
                queueid = command_dict.get(b'i', None)
                if queueid:
                    self.queueid = force_uString(queueid)
                    logging.getLogger('fuglu.MilterHandler.queueid').info(
                        '"%s" "%s"' % (self.id, self.queueid))

            if not self.sasl_login:
                sasl_login = command_dict.get(b'auth_authen', None)
                if sasl_login:
                    self.sasl_login = force_uString(sasl_login)

            if not self.sasl_sender:
                sasl_sender = command_dict.get(b'auth_author', None)
                if sasl_sender:
                    self.sasl_sender = force_uString(sasl_sender)

            if not self.sasl_method:
                sasl_method = command_dict.get(b'auth_type', None)
                if sasl_method:
                    self.sasl_method = force_uString(sasl_method)
            if not self.ptr:
                ptr = command_dict.get(b'_', None)
                if ptr:
                    try:
                        self.ptr = force_uString(ptr).split(maxsplit=1)[0]
                    except Exception:
                        pass
            if not self.cipher:
                cipher = command_dict.get(b'cipher', None)
                if cipher:
                    self.cipher = cipher
            if not self.cipher_bits:
                cipher_bits = command_dict.get(b'cipher_bits', None)
                if cipher_bits:
                    self.cipher_bits = cipher_bits
            if not self.cert_subject:
                cert_subject = command_dict.get(b'cert_subject', None)
                if cert_subject:
                    self.cert_subject = cert_subject
            if not self.cert_issuer:
                cert_issuer = command_dict.get(b'cert_issuer', None)
                if cert_issuer:
                    self.cert_issuer = cert_issuer
            if not self.tls_version:
                tls_version = command_dict.get(b'tls_version', None)
                if tls_version:
                    self.tls_version = tls_version

    @staticmethod
    def dict_unicode(command_dict):
        commanddictstring = u""
        if command_dict:
            for key,value in iter(command_dict.items()):
                commanddictstring += force_uString(key) + u": " + force_uString(value) + u", "
        return commanddictstring

    async def connect(self, hostname, family, ip, port, command_dict):
        from fuglu.mshared import BasicMilterPlugin, BMPConnectMixin

        self.log('Connect from %s:%d (%s) with family: %s, dict: %s' % (ip, port,
                                                              hostname, family, str(command_dict)))
        self.store_info_from_dict(command_dict)
        if family not in (b'4', b'6', b"U"):
            self.logger.warning('Return temporary fail since family is: %s' % force_uString(family))
            self.logger.warning(u'command dict is: %s' % MilterSession.dict_unicode(command_dict))
            return lm.TEMPFAIL
        elif family == b"U":
            # we handle unix socket, but print debug message since it's not tested well
            self.logger.debug(f'Handle unix socket connection')
        if hostname is None or force_uString(hostname) == u'[%s]' % force_uString(ip):
            hostname = u'unknown'

        self.fcrdns = hostname
        self.addr = ip

        # report connection info in case there's an early postfix reject it's
        # at least possible to link the id to a connection
        self.logger.info(f'{self.id} ({CONNECT}) '
                         f'ip:{force_uString(self.addr, convert_none=True)}, '
                         f'fcrdns:{force_uString(self.fcrdns, convert_none=True)}, '
                         f'ptr:{force_uString(self.ptr, convert_none=True)}')

        plugins = self.mhandler.milterplugins.get(CONNECT, [])
        self.log(f"{self.id} Plugins({CONNECT}): {plugins}")

        self.mhandler.tracktime(f"Before-MPlugins({CONNECT})")
        # ---
        # run plugins
        # ---
        for plug in plugins:
            plug: tp.Union[BasicMilterPlugin, BMPConnectMixin]
            # check if plugin can run async
            iscoroutine = asyncio.iscoroutinefunction(plug.examine_connect)
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} (async={iscoroutine}) {CONNECT}-Plugin: {plug} -> skip on tag request")
                continue

            inexecutor = (not iscoroutine) and bool(self.mhandler.pool)
            msg = f"{self.id} Running(async={iscoroutine}/p={inexecutor}) {CONNECT}-Plugin: {plug}"
            self.mhandler.set_workerstate(msg)
            self.logger.debug(msg)

            # run plugin (async if possible)
            if iscoroutine:
                res = await plug.examine_connect(sess=self, host=self.fcrdns, addr=self.addr)
            elif inexecutor:
                # run in pool
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(self.mhandler.pool,
                                                 functools.partial(plug.examine_connect,
                                                                   sess=self,
                                                                   host=self.fcrdns,
                                                                   addr=self.addr
                                                                   )
                                                 )
            else:
                res = plug.examine_connect(sess=self, host=self.fcrdns, addr=self.addr)
            # override action
            res = plug._check_apply_override_milter(res, self.id)
            # process reply
            res, msg, retcode = await self.handle_milter_plugin_reply(res, fugluid=self.id)

            # plugin timing
            self.mhandler.tracktime(f"{plug}({CONNECT})", mplugin=True)

            # return directly if plugin answer is not lm.CONTINUE
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {CONNECT}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                if res not in RETCODE2STR.keys():
                    self.logger.info(f"{self.id} {CONNECT}-Plugin {plug} returns unknown result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                    return lm.TEMPFAIL
                return retcode

        return lm.CONTINUE

    async def helo(self, helo_name, command_dict):
        from fuglu.mshared import BasicMilterPlugin, BMPHeloMixin

        self.log(f'HELO: {helo_name}, dict: {str(command_dict)}')
        self.store_info_from_dict(command_dict)
        self.heloname = force_uString(helo_name)

        # report helo in case there's an early postfix reject it's
        # at least possible to link the id to a helo
        self.logger.info(f'{self.id} ({HELO}) helo:{force_uString(self.heloname, convert_none=True)}')

        plugins = self.mhandler.milterplugins.get(HELO, [])
        self.log(f"{self.id} Plugins({HELO}): {plugins}")
        self.mhandler.tracktime(f"Before-MPlugins({HELO})")

        # ---
        # run plugins
        # ---
        for plug in plugins:
            plug: tp.Union[BasicMilterPlugin, BMPHeloMixin]
            # check if plugin can run async
            iscoroutine = asyncio.iscoroutinefunction(plug.examine_helo)
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} (async={iscoroutine}) {HELO}-Plugin: {plug} -> skip on tag request")
                continue

            inexecutor = (not iscoroutine) and bool(self.mhandler.pool)
            msg = f"{self.id} Running(async={iscoroutine}/p={inexecutor}) {HELO}-Plugin: {plug}"
            self.mhandler.set_workerstate(msg)
            self.logger.debug(msg)

            # run plugin (async if possible)
            if iscoroutine:
                res = await plug.examine_helo(sess=self, helo=self.heloname)
            elif inexecutor:
                # run in pool
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(self.mhandler.pool,
                                                 functools.partial(plug.examine_helo,
                                                                   sess=self,
                                                                   helo=self.heloname
                                                                   )
                                                 )
            else:
                res = plug.examine_helo(sess=self, helo=self.heloname)

            # override action
            res = plug._check_apply_override_milter(res, self.id)
            # process reply
            res, msg, retcode = await self.handle_milter_plugin_reply(res, fugluid=self.id)

            # plugin timing
            self.mhandler.tracktime(f"{plug}({HELO})", mplugin=True)

            # return directly if plugin answer is not lm.CONTINUE
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {HELO}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                if res not in RETCODE2STR.keys():
                    self.logger.info(f"{self.id} {HELO}-Plugin {plug} returns unknown result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                    return lm.TEMPFAIL
                return retcode
        return lm.CONTINUE

    async def mailFrom(self, from_address, command_dict):
        from fuglu.mshared import BasicMilterPlugin, BMPMailFromMixin

        # store exactly what was received
        self.log('FROM_ADDRESS: %s, dict: %s' % (from_address, MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)

        from_address = self._clean_address(from_address)

        from_address_string = force_uString(from_address, convert_none=True)
        if from_address_string and not Addrcheck().valid(from_address_string):
            from fuglu.mshared import retcode2milter
            self.logger.warning(f"{self.id} Invalid sender address: {from_address_string}")
            failmessage = self.mhandler.config.get("main",
                                                   "address_compliance_fail_message", "")
            if not failmessage:
                failmessage = f"Invalid sender address: {from_address_string}"

            failaction = self.mhandler.config.get("main",
                                                  "address_compliance_fail_action",
                                                  f"dunno")

            res = string_to_actioncode(failaction)
            res = retcode2milter[res]

            res, msg, retcode = await self.handle_milter_plugin_reply((res, failmessage), fugluid=self.id)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {MAILFROM}-AddressCheck returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                return retcode

        self.sender = from_address
        plugins = self.mhandler.milterplugins.get(MAILFROM, [])
        self.log(f"{self.id} Plugins({MAILFROM}): {plugins}")
        self.mhandler.tracktime(f"Before-MPlugins({MAILFROM})")

        # ---
        # run plugins
        # ---
        for plug in plugins:
            plug: tp.Union[BasicMilterPlugin, BMPMailFromMixin]
            # check if plugin can run async
            iscoroutine = asyncio.iscoroutinefunction(plug.examine_mailfrom)
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} (async={iscoroutine}) {MAILFROM}-Plugin: {plug} -> skip on tag request")
                continue

            inexecutor = (not iscoroutine) and bool(self.mhandler.pool)
            msg = f"{self.id} Running(async={iscoroutine}/p={inexecutor}) {MAILFROM}-Plugin: {plug}"
            self.mhandler.set_workerstate(msg)
            self.logger.debug(msg)

            # run plugin (async if possible)
            if iscoroutine:
                res = await plug.examine_mailfrom(sess=self, sender=self.sender)
            elif inexecutor:
                # run in pool
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(self.mhandler.pool,
                                                 functools.partial(plug.examine_mailfrom,
                                                                   sess=self,
                                                                   sender=self.sender,
                                                                   )
                                                 )
            else:
                res = plug.examine_mailfrom(sess=self, sender=self.sender)

            # override action
            res = plug._check_apply_override_milter(res, self.id)
            # process reply
            res, msg, retcode = await self.handle_milter_plugin_reply(res, fugluid=self.id)

            # plugin timing
            self.mhandler.tracktime(f"{plug}({MAILFROM})", mplugin=True)

            # return directly if plugin answer is not lm.CONTINUE
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {MAILFROM}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                if res not in RETCODE2STR.keys():
                    self.logger.info(f"{self.id} {MAILFROM}-Plugin {plug} returns unknown result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                    return lm.TEMPFAIL
                return retcode
        return lm.CONTINUE

    async def rcpt(self, recipient, command_dict):
        from fuglu.mshared import BasicMilterPlugin, BMPRCPTMixin

        # store exactly what was received
        self.log('RECIPIENT: %s, dict: %s' % (recipient, MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)
        recipient = self._clean_address(recipient)

        recipient_string = force_uString(recipient, convert_none=True)
        if recipient_string and not Addrcheck().valid(recipient_string, allow_postmaster=True):
            from fuglu.mshared import retcode2milter
            self.logger.warning(f"{self.id} Invalid recipient address: {recipient_string}")
            failmessage = self.mhandler.config.get("main",
                                                   "address_compliance_fail_message", "")
            if not failmessage:
                failmessage = f"Invalid recipient address: {recipient_string}"

            failaction = self.mhandler.config.get("main",
                                                  "address_compliance_fail_action",
                                                  f"dunno")
            res = string_to_actioncode(failaction)
            res = retcode2milter[res]

            res, msg, retcode = await self.handle_milter_plugin_reply((res, failmessage), fugluid=self.id)
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {RCPT}-AddressCheck returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                return retcode

        if recipient is not None:
            self.recipients.append(recipient)
        plugins = self.mhandler.milterplugins.get(RCPT, [])
        self.log(f"{self.id} Plugins({RCPT}): {plugins}")
        self.mhandler.tracktime(f"Before-MPlugins({RCPT})")

        # ---
        # run plugins
        # ---
        for plug in plugins:
            plug: tp.Union[BasicMilterPlugin, BMPRCPTMixin]
            iscoroutine = asyncio.iscoroutinefunction(plug.examine_rcpt)
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} (async={iscoroutine}) {RCPT}-Plugin: {plug} -> skip on tag request")
                continue

            inexecutor = (not iscoroutine) and bool(self.mhandler.pool)
            msg = f"{self.id} Running(async={iscoroutine}/p={inexecutor}) {RCPT}-Plugin: {plug}"
            self.mhandler.set_workerstate(msg)
            self.logger.debug(msg)

            # run plugin (async if possible)
            if iscoroutine:
                res = await plug.examine_rcpt(sess=self, recipient=recipient)
            elif inexecutor:
                # run in pool
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(self.mhandler.pool,
                                                 functools.partial(plug.examine_rcpt,
                                                                   sess=self,
                                                                   recipient=recipient,
                                                                   )
                                                 )
            else:
                res = plug.examine_rcpt(sess=self, recipient=recipient)

            # override action
            res = plug._check_apply_override_milter(res, self.id)
            # process reply
            res, msg, retcode = await self.handle_milter_plugin_reply(res, fugluid=self.id)

            # plugin timing
            self.mhandler.tracktime(f"{plug}({RCPT})", mplugin=True)

            # return directly if plugin answer is not lm.CONTINUE
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {RCPT}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                if res not in RETCODE2STR.keys():
                    self.logger.info(f"{self.id} {RCPT}-Plugin {plug} returns unknown result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                    return lm.TEMPFAIL
                return retcode

        return lm.CONTINUE

    async def header(self, key, val, command_dict):
        from fuglu.mshared import BasicMilterPlugin, BMPHeaderMixin

        self.log('HEADER, KEY: %s, VAL: %s, dict: %s' % (key, val, MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)
        self.buffer.write(key+b": "+val+b"\n")
        # backup original headers
        self.original_headers.append((key, val))
        plugins = self.mhandler.milterplugins.get(HEADER, [])
        self.log(f"{self.id} Plugins({HEADER}): {plugins}")
        self.mhandler.tracktime(f"Before-MPlugins({HEADER})")

        # ---
        # run plugins
        # ---
        for plug in plugins:
            plug: tp.Union[BasicMilterPlugin, BMPHeaderMixin]
            # check if plugin can run async
            iscoroutine = asyncio.iscoroutinefunction(plug.examine_header)
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} (async={iscoroutine}) {HEADER}-Plugin: {plug} -> skip on tag request")
                continue

            inexecutor = (not iscoroutine) and bool(self.mhandler.pool)
            msg = f"{self.id} Running(async={iscoroutine}/p={inexecutor}) {HEADER}-Plugin: {plug}"
            self.mhandler.set_workerstate(msg)
            self.logger.debug(msg)

            # run plugin (async if possible)
            if iscoroutine:
                res = await plug.examine_header(sess=self, key=key, value=val)
            elif inexecutor:
                # run in pool
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(self.mhandler.pool,
                                                 functools.partial(plug.examine_header,
                                                                   sess=self,
                                                                   key=key,
                                                                   value=val
                                                                   )
                                                 )
            else:
                res = plug.examine_header(sess=self, key=key, value=val)

            # override action
            res = plug._check_apply_override_milter(res, self.id)
            # process reply
            res, msg, retcode = await self.handle_milter_plugin_reply(res, fugluid=self.id)

            # plugin timing
            self.mhandler.tracktime(f"{plug}({HEADER})", mplugin=True)

            # return directly if plugin answer is not lm.CONTINUE
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {HEADER}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                if res not in RETCODE2STR.keys():
                    self.logger.info(f"{self.id} {HEADER}-Plugin {plug} returns unknown result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                    return lm.TEMPFAIL
                return retcode

        return lm.CONTINUE

    async def eoh(self, command_dict):
        from fuglu.mshared import BasicMilterPlugin, BMPEOHMixin

        self.log('EOH, dict: %s' % MilterSession.dict_unicode(command_dict))
        self.store_info_from_dict(command_dict)
        self.buffer.write(b"\n")
        plugins = self.mhandler.milterplugins.get(EOH, [])
        self.log(f"{self.id} Plugins({EOH}): {plugins}")
        self.mhandler.tracktime(f"Before-MPlugins({EOH})")

        # ---
        # run plugins
        # ---
        for plug in plugins:
            plug: tp.Union[BasicMilterPlugin, BMPEOHMixin]
            # check if plugin can run async
            iscoroutine = asyncio.iscoroutinefunction(plug.examine_eoh)
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} (async={iscoroutine}) {EOH}-Plugin: {plug} -> skip on tag request")
                continue

            inexecutor = (not iscoroutine) and bool(self.mhandler.pool)
            msg = f"{self.id} Running(async={iscoroutine}/p={inexecutor}) {EOH}-Plugin: {plug}"
            self.mhandler.set_workerstate(msg)
            self.logger.debug(msg)

            # run plugin (async if possible)
            if iscoroutine:
                res = await plug.examine_eoh(sess=self)
            elif inexecutor:
                # run in pool
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(self.mhandler.pool,
                                                 functools.partial(plug.examine_eoh,
                                                                   sess=self
                                                                   )
                                                 )
            else:
                res = plug.examine_eoh(sess=self)

            # override action
            res = plug._check_apply_override_milter(res, self.id)
            # process reply
            res, msg, retcode = await self.handle_milter_plugin_reply(res, fugluid=self.id)

            # plugin timing
            self.mhandler.tracktime(f"{plug}({EOH})", mplugin=True)

            # return directly if plugin answer is not lm.CONTINUE
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {EOH}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                if res not in RETCODE2STR.keys():
                    self.logger.info(f"{self.id} {EOH}-Plugin {plug} returns unknown result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                    return lm.TEMPFAIL
                return retcode
        return lm.CONTINUE

    async def data(self, command_dict):
        self.log('DATA, dict: %s' % MilterSession.dict_unicode(command_dict))
        self.store_info_from_dict(command_dict)
        return lm.CONTINUE

    @lm.noReply
    async def body(self, chunk, command_dict):
        self.log('BODY chunk: %d, dict: %s' % (len(chunk), MilterSession.dict_unicode(command_dict)))
        self.store_info_from_dict(command_dict)
        self.buffer.write(chunk)
        return lm.CONTINUE

    async def eob(self, command_dict):
        from fuglu.mshared import BasicMilterPlugin, BMPEOBMixin

        self.log('EOB dict: %s' % MilterSession.dict_unicode(command_dict))
        self.store_info_from_dict(command_dict)

        # increase message counter for this session
        self.imessage += 1

        # ---
        # run plugins
        # ---
        plugins = self.mhandler.milterplugins.get(EOB, [])
        self.log(f"{self.id} Plugins({EOB}): {plugins}")
        self.mhandler.tracktime(f"Before-MPlugins({EOB})")

        for plug in plugins:
            plug: tp.Union[BasicMilterPlugin, BMPEOBMixin]
            # check if plugin can run async
            iscoroutine = asyncio.iscoroutinefunction(plug.examine_eob)
            if self.skip_plugin(plugin=plug):
                self.logger.info(f"{self.id} (async={iscoroutine}) {EOB}-Plugin: {plug} -> skip on tag request")
                continue

            inexecutor = (not iscoroutine) and bool(self.mhandler.pool)
            msg = f"{self.id} Running(async={iscoroutine}/p={inexecutor}) {EOB}-Plugin: {plug}"
            self.mhandler.set_workerstate(msg)
            self.logger.debug(msg)

            # run plugin (async if possible)
            if iscoroutine:
                res = await plug.examine_eob(sess=self)
            elif inexecutor:
                # run in pool
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(self.mhandler.pool,
                                                 functools.partial(plug.examine_eob,
                                                                   sess=self
                                                                   )
                                                 )
            else:
                res = plug.examine_eob(sess=self)

            # override action
            res = plug._check_apply_override_milter(res, self.id)
            # process reply
            res, msg, retcode = await self.handle_milter_plugin_reply(res, fugluid=self.id)

            # plugin timing
            self.mhandler.tracktime(f"{plug}({EOB})", mplugin=True)

            # return directly if plugin answer is not lm.CONTINUE
            if not res == lm.CONTINUE:
                self.logger.info(f"{self.id} {EOB}-Plugin {plug} returns non-continue-result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}, msg: {msg}")
                if res not in RETCODE2STR.keys():
                    self.logger.info(f"{self.id} {EOB}-Plugin {plug} returns unknown result: {RETCODE2STR.get(res,f'unknown(orig:{res})')}")
                    return lm.TEMPFAIL
                return retcode

        # default milter reply code for basic plugins
        replycode = lm.CONTINUE

        # if there is a milter handler and there are plugins,
        # create a suspect and run normal plugin handler
        if self.mhandler and (self.mhandler.plugins or self.mhandler.appenders):

            self.mhandler.tracktime(f"Before handling base plugins")
            msg = f"{self.id} Running base plugins on full Suspect"
            self.mhandler.set_workerstate(msg)

            from_address = self.get_cleaned_from_address()
            recipients = self.get_cleaned_recipients()
            temp_filename = None

            # extra suspect params
            kwargs = {
                "tmpdir": self.mhandler.config.get('main', 'tempdir')
            }
            if self.mhandler._att_mgr_cachesize:
                kwargs['att_mgr_cachesize'] = self.mhandler._att_mgr_cachesize
            if self.mhandler._att_defaultlimit:
                kwargs['att_defaultlimit'] = self.mhandler._att_defaultlimit
            if self.mhandler._att_maxlimit:
                kwargs['att_maxlimit'] = self.mhandler._att_maxlimit


            suspect = Suspect(force_uString(from_address),
                              force_uString(recipients),
                              temp_filename,
                              sasl_login=self.sasl_login,
                              sasl_sender=self.sasl_sender,
                              sasl_method=self.sasl_method,
                              queue_id=self.queueid,
                              inbuffer=bytes(self._buffer.getbuffer()),
                              id=self.id, **kwargs)
            
            self.mhandler.tracktime(f"Suspect created")
            suspect.timestamp = self.timestamp

            # add headers
            for hdrname, hdrval in self.addheaders.items():
                suspect.add_header(key=hdrname, value=hdrval, immediate=False)

            # add session tags to Suspect
            if self.tags:
                suspect.tags.update(self.tags)

            if self.heloname is not None and self.addr is not None and self.fcrdns is not None:
                suspect.clientinfo = force_uString(self.heloname), force_uString(self.addr), force_uString(self.fcrdns)

            suspect.tags['incomingport'] = self.mhandler.port

            message_prefix = f"(#{self.imessage})"

            if self.mhandler.pool:
                # run in pool
                loop = asyncio.get_event_loop()
                self.logger.debug("Run prependers in Threadpool-executor")
                pluglist, applist = await loop.run_in_executor(self.mhandler.pool, self.mhandler.run_prependers, suspect)
                # run plugins
                self.logger.debug("Run Suspect plugins in Threadpool-executor")
                result, msg = await loop.run_in_executor(self.mhandler.pool,
                                                         functools.partial(self.mhandler.run_suspect_plugins,
                                                                           pluglist=pluglist,
                                                                           suspect=suspect,
                                                                           message_prefix=message_prefix
                                                                           )
                                                         )
            else:
                pluglist, applist = self.mhandler.run_prependers(suspect)
                # run plugins
                result, msg = self.mhandler.run_suspect_plugins(pluglist=pluglist, suspect=suspect, message_prefix=message_prefix)

            message_is_deferred = False
            if result == ACCEPT or result == DUNNO:
                try:
                    await self.modifiy_msg_as_requested(suspect)
                    self.mhandler.tracktime("Modify-msg-as-requested")
                except Exception as e:
                    message_is_deferred = True
                    trb = traceback.format_exc()
                    self.logger.error("Could not commit message. Error: %s" % trb)
                    self.logger.exception(e)
                    await self._defer()
                    # reply with Deferred object (which does nothing) because we've already
                    # sent a reply
                    replycode = lm.Deferred()

            elif result == DELETE:
                self.logger.info("MESSAGE DELETED: %s" % suspect.id)
                retmesg = 'OK: (%s)' % suspect.id
                if msg is not None:
                    retmesg = msg
                await self.discard(retmesg)
                # reply with Deferred object (which does nothing) because we've already
                # sent a reply
                replycode = lm.Deferred()
            elif result == REJECT:
                retmesg = "Rejected by content scanner"
                if msg is not None:
                    retmesg = msg
                retmesg = "%s (%s)" % (retmesg, suspect.id)
                await self.reject(retmesg)
                # reply with Deferred object (which does nothing) because we've already
                # sent a reply
                replycode = lm.Deferred()
            elif result == DEFER:
                message_is_deferred = True
                await self._defer(msg)
                # reply with Deferred object (which does nothing) because we've already
                # sent a reply
                replycode = lm.Deferred()
            else:
                self.logger.error(
                    'Invalid Message action Code: %s. Using DEFER' % result)
                message_is_deferred = True
                await self._defer()
                # reply with Deferred object (which does nothing) because we've already
                # sent a reply
                replycode = lm.Deferred()

            # run appenders (stats plugin etc) unless msg is deferred
            if not message_is_deferred:
                if self.mhandler.pool:
                    loop = asyncio.get_event_loop()
                    self.logger.debug("Run Suspect appenders in Threadpool-executor")
                    await loop.run_in_executor(self.mhandler.pool,
                                               self.mhandler.run_appenders, suspect, result, applist)
                else:
                    self.mhandler.run_appenders(suspect, result, applist)
            else:
                self.logger.warning("DEFERRED %s" % suspect.id)

            # clean up
            try:
                # dump buffer to temp file
                self.buffer = None
            except Exception as e:
                self.logger.exception(e)
                pass

            try:
                if suspect.inbuffer:
                    del suspect.inbuffer
                del suspect
            except Exception as e:
                self.logger.exception(e)
                pass

            msg = f"{self.id} Suspect analysis complete"
            self.mhandler.set_workerstate(msg)

        self.mhandler.report_timings(suspectid=self.id, withrealtime=True)
        self.mhandler.resettimer()
        self.id = None
        return replycode

    async def _defer(self, message=None):
        if message is None:
            message = "internal problem - message deferred"

        # try to end the session gracefully, but this might cause the same exception again,
        # in case of a broken pipe for example
        try:
            await self.defer(message)
        except Exception:
            pass

    async def close(self):
        # close the socket
        self.log('Close')
        if self.writer:
            try:
                self.writer.close()
                self.writer = None
            except Exception as e:
                self.logger.warning(f"while socket shutdown: {e}")

        # close the tempfile
        try:
            # close buffer directly without dumping file
            self._buffer = None
        except Exception as e:
            self.logger.error("closing tempfile: %s" % str(e))
            pass

    async def abort(self):
        self.logger.debug('Abort has been called')
        self.reset_connection()

    async def replacebody(self, newbody):
        """
        Replace message body sending corresponding command to MTA
        using protocol stored in self

        Args:
            newbody (string(encoded)): new message body
        """
        # check if option is available
        if not self.has_option(lm.SMFIF_CHGBODY):
            self.logger.error('Change body called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.has_option(lm.SMFIF_CHGBODY, client="fuglu"),
                               self.has_option(lm.SMFIF_CHGBODY, client="mta")))
            return
        await self.replBody(force_bString(newbody))

    async def addheader(self, key, value):
        """
        Add header in message sending corresponding command to MTA
        using protocol stored in self

        Args:
            key (string(encoded)): header key
            value (string(encoded)): header value
        """
        if not self.has_option(lm.SMFIF_ADDHDRS):
            self.logger.error('Add header called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.has_option(lm.SMFIF_ADDHDRS, client="fuglu"),
                               self.has_option(lm.SMFIF_ADDHDRS, client="mta")))
            return
        await self.addHeader(force_bString(key), force_bString(value))

    async def changeheader(self, key, value):
        """
        Change header in message sending corresponding command to MTA
        using protocol stored in self

        Args:
            key (string(encoded)): header key
            value (string(encoded)): header value
        """
        if not self.has_option(lm.SMFIF_CHGHDRS):
            self.logger.error('Change header called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.has_option(lm.SMFIF_CHGHDRS, client="fuglu"),
                               self.has_option(lm.SMFIF_CHGHDRS, client="mta")))
            return
        await self.chgHeader(force_bString(key), force_bString(value))

    async def change_from(self, from_address):
        """
        Change envelope from mail address.
        Args:
            from_address (unicode,str): new from mail address
        """
        if not self.has_option(lm.SMFIF_CHGFROM):
            self.logger.error('Change from called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.has_option(lm.SMFIF_CHGFROM, client="fuglu"),
                               self.has_option(lm.SMFIF_CHGFROM, client="mta")))
            return
        await self.chgFrom(force_bString(from_address))

    async def add_rcpt(self, rcpt):
        """
        Add a new envelope recipient
        Args:
            rcpt (str, unicode): new recipient mail address, with <> qualification
        """
        if not self.has_option(lm.SMFIF_ADDRCPT_PAR):
            self.logger.error('Add rcpt called without the proper opts set, '
                              'availability -> fuglu: %s, mta: %s' %
                              (self.has_option(lm.SMFIF_ADDRCPT_PAR, client="fuglu"),
                               self.has_option(lm.SMFIF_ADDRCPT_PAR, client="mta")))
            return
        await self.addRcpt(force_bString(rcpt))

    async def endsession(self):
        """Close session"""
        try:
            await self.close()
        except Exception:
            pass

    async def remove_recipients(self):
        """
        Remove all the original envelope recipients
        """
        # use the recipient data from the session because
        # it has to match exactly
        for recipient in self.recipients:
            self.logger.debug("Remove env recipient: %s" % force_uString(recipient))
            await self.delRcpt(recipient)
        self.recipients = []

    async def remove_headers(self):
        """
        Remove all original headers
        """
        for key, value in self.original_headers:
            self.logger.debug("Remove header-> %s: %s" % (force_uString(key), force_uString(value)))
            await self.changeheader(key, b"")
        self.original_headers = []

    async def modifiy_msg_as_requested(self, suspect):
        """
        Commit message. Modify message if requested.
        Args:
            suspect (fuglu.shared.Suspect): the suspect

        """
        if not self.mhandler:
            return

        if self.mhandler.enable_mode_readonly:
            return

        if self.mhandler.replace_demo:
            msg = suspect.get_message_rep()
            from_address = msg.get("From", "unknown")
            to_address = msg.get("To", "unknown")
            suspect.set_message_rep(MilterSession.replacement_mail(from_address, to_address))
            self.logger.warning("Replace message by dummy template...")
            self.enable_mode_tags = True
            suspect.set_tag('milter_replace', 'all')

        # --------------- #
        # modifications   #
        # --------------- #
        replace_headers = False
        replace_body = False
        replace_from = False
        replace_to = False

        # --
        # check for changes if automatic mode is enabled
        # --
        if self.mhandler.enable_mode_auto:
            replace_headers = False
            replace_body = suspect.is_modified()
            replace_from = suspect.orig_from_address_changed()
            replace_to = suspect.orig_recipients_changed()
            self.logger.debug("Mode auto -> replace headers:%s, body:%s, from:%s, to:%s" %
                              (replace_headers, replace_body, replace_from, replace_to))

        # --
        # apply milter options from config
        # --
        if self.mhandler.enable_mode_manual and self.mhandler.milter_mode_options:
            if "all" in self.mhandler.milter_mode_options:
                replace_headers = True
                replace_body = True
                replace_from = True
                replace_to = True
            if "body" in self.mhandler.milter_mode_options:
                replace_body = True
            if "headers" in self.mhandler.milter_mode_options:
                replace_headers = True
            if "from" in self.mhandler.milter_mode_options:
                replace_from = True
            if "to" in self.mhandler.milter_mode_options:
                replace_from = True
            self.logger.debug("Mode options -> replace headers:%s, body:%s, from:%s, to:%s" %
                              (replace_headers, replace_body, replace_from, replace_to))

        # --
        # apply milter options from tags (which can be set by plugins)
        # --
        if self.mhandler.enable_mode_tags:
            milter_replace_tag = suspect.get_tag('milter_replace')
            if milter_replace_tag:
                milter_replace_tag = milter_replace_tag.lower()
                if "all" in milter_replace_tag:
                    replace_headers = True
                    replace_body = True
                    replace_from = True
                    replace_to = True
                if "body" in milter_replace_tag:
                    replace_body = True
                if "headers" in milter_replace_tag:
                    replace_headers = True
                if "from" in milter_replace_tag:
                    replace_from = True
                if "to" in milter_replace_tag:
                    replace_from = True
                self.logger.debug("Mode tags -> replace headers:%s, body:%s, from:%s, to:%s" %
                                  (replace_headers, replace_body, replace_from, replace_to))

        # ----------------------- #
        # replace data in message #
        # ----------------------- #
        if replace_from:
            self.logger.warning(f"{suspect.id} Set new envelope \"from address\": {suspect.from_address}")
            await self.change_from(suspect.from_address)

        if replace_to:
            # remove original recipients
            await self.remove_recipients()

            # add new recipients, use list in suspect
            self.logger.warning(f"{suspect.id} Reset to {len(suspect.recipients)} envelope recipient(s)")
            for recipient in suspect.recipients:
                await self.add_rcpt(recipient)

        if self.mhandler.enable_mode_auto and not replace_headers:
            self.logger.warning(f"{suspect.id} Modify({len(suspect.added_headers)})/add({len(suspect.modified_headers)}"
                                f" headers according to modification track in suspect")
            for key, val in iter(suspect.added_headers.items()):
                hdr = Header(val, header_name=key, continuation_ws=' ')
                await self.addheader(key, hdr.encode())

            for key, val in iter(suspect.modified_headers.items()):
                hdr = Header(val, header_name=key, continuation_ws=' ')
                await self.changeheader(key, hdr.encode())

        if replace_headers:
            self.logger.warning(f"{suspect.id} Remove {len(self.original_headers)} original headers ")
            await self.remove_headers()

            msg = suspect.get_message_rep()
            self.logger.warning(f"Add {len(msg)} headers from suspect mail")
            for key, val in iter(msg.items()):
                self.logger.debug("Add header from msg-> %s: %s" % (key, val))
                hdr = Header(val, header_name=key, continuation_ws=' ')
                await self.addheader(key, hdr.encode())
        # --
        # headers to add, same as for the other connectors
        # --
        self.logger.info(f"{suspect.id} Add {len(suspect.addheaders)} headers as defined in suspect")
        for key, val in iter(suspect.addheaders.items()):
            hdr = Header(val, header_name=key, continuation_ws=' ')
            self.logger.debug("Add suspect header-> %s: %s" % (key, val))
            await self.addheader(key, hdr.encode())

        if replace_body:
            self.logger.warning(f"{suspect.id} Replace message body")
            msg_string = suspect.get_message_rep().as_string()
            # just dump everything below the headers
            newbody = msg_string[msg_string.find("\n\n")+len("\n\n"):]
            self.logger.info(f"{suspect.id} Replace with new body of size: {len(newbody)}")

            await self.replacebody(newbody)

    @staticmethod
    def replacement_mail(from_address, to_address):
        """
        Create a mail replacing the whole original mail. This
        is for testing purposes...

        Args:
            from_address (str): New address for 'From' header
            to_address (str):  New address for 'To' header

        Returns:
            email: Python email representation

        """
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Replacement message info"
        msg['From'] = from_address
        msg['To'] = to_address

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nBad luck, your message has been replaced completely :-("
        html = u"""\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               Bad luck!<br>
               Your message has been replaced completely &#9785
            </p>
          </body>
        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html', _charset="UTF-8")

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        return msg

    async def defer(self, reason):
        """
        Defer mail.
        Args:
            reason (str,unicode): Defer message
        """
        await self.send_reply_message(450, "", reason)

        self.logger.debug("defer message, reason: %s" % reason)

    async def reject(self, reason):
        """
        Reject mail.
        Args:
            reason (str,unicode): Reject message
        """
        await self.send_reply_message(550, "", reason)
        self.logger.debug("reject message, reason: %s" % reason)

    async def discard(self, reason: str):
        """
        Discard mail.
        Args:
            reason (str,unicode): Defer message, only for internal logging
        """
        await self.send(lm.DISCARD)
        self.logger.debug("discard message, reason: %s" % reason)


class ProcLocalDict(object):
    """
    Process singleton to store a default dictionary instance
    """

    _instance = None
    procPID = None

    @classmethod
    def instance(cls) -> tp.Dict:
        pid = os.getpid()
        logger = logging.getLogger("%s.CacheSingleton" % __package__)
        if pid == ProcLocalDict.procPID and ProcLocalDict.instance is not None:
            logger.debug("Return existing Cache Singleton for process with pid: %u"%pid)
        else:
            if ProcLocalDict.instance is None:
                logger.info("Create ProcLocalDict for process with pid: %u"%pid)
            elif ProcLocalDict.procPID != pid:
                logger.warning(f"Replace ProcLocalDict(created by process {ProcLocalDict.procPID}) for process with pid: {pid}")

            ProcLocalDict._instance = dict()
            ProcLocalDict.procPID = pid
        return cls._instance


class MilterServer:
    def __init__(self, controller, port=10125, address="127.0.0.1", protohandlerclass=None):
        #BasicTCPServer.__init__(self, controller, port, address, MilterHandler)
        if protohandlerclass is None:
            protohandlerclass = ProtocolHandler
        self.protohandlerclass = protohandlerclass
        self.logger = logging.getLogger("fuglu.incoming.%s" % port)
        self.logger.debug('Starting incoming Server on Port %s, protocol=%s' % (
            port, self.protohandlerclass.protoname))
        self.logger.debug('Incoming server process info:  %s' % createPIDinfo())
        self.logger.debug('(%s) Logger id is %s' % (createPIDinfo(),id(self)))
        self.port = port
        self.controller = controller
        self.stayalive = True
        self.srv = None
        self.addr_f = socket.getaddrinfo(address, 0)[0][0]
        self.address = address

    @staticmethod
    async def client_connected(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        from fuglu.asyncprocpool import ProcManager
        from fuglu.core import MainController
        milterserver = ProcLocalDict.instance()['milterserver']

        controller: MainController = milterserver.controller
        asyncprocpool: ProcManager = controller.asyncprocpool
        if controller.asyncprocpool:
            milterserver.logger.debug(f"Create task:\n"
                                      f"- reader:{reader}\n"
                                      f"- writer:{writer}\n"
                                      f"- socket:{writer.get_extra_info('socket')}")
            asyncprocpool.add_task_from_socket(writer.get_extra_info('socket'), 'asyncmilterconnector', 'MilterHandler', milterserver.port)
        else:
            # create milter handler
            mhand = MilterHandler(milterserver.controller.config,
                                  milterserver.controller.prependers,
                                  milterserver.controller.plugins,
                                  milterserver.controller.appenders,
                                  milterserver.port,
                                  milterserver.controller.milterdict)

            # create milter session, passing handler
            msess = MilterSession(reader, writer, milterserver.controller.config,
                                  options=mhand.sess_options, mhandler=mhand)
            # handle session
            await msess.handlesession()
            del msess
            del mhand

    def shutdown(self):
        self.logger.info(f"TCP Server on port {self.port} closing")
        self.stayalive = False
        try:
            loop = asyncio.get_event_loop()
            self.srv.close()
            loop.run_until_complete(self.srv.wait_closed())
            self.logger.debug(f"TCP Server on port {self.port}: closed (after waiting)")

        except Exception as e:
            self.logger.debug(f"TCP Server on port {self.port}: server loop closed error={e}")
            pass

    def serve(self):
        self.logger.info(f'AsyncMilter Server running on port {self.port}')

        ProcLocalDict.instance()['milterserver'] = self

        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(MilterServer.client_connected, host=self.address, port=self.port, loop=loop, family=self.addr_f)
        self.logger.info('Started incoming Server on %s:%s' % (self.address, self.port))
        self.srv = loop.run_until_complete(coro)
        self.logger.info('Completed incoming Server on %s:%s' % (self.address, self.port))

# async def mp_queue_wait(mp_q: multiprocessing.Queue, executor=None):
#     """Helper routine to combine waiting for element in multiprocessing queue with asyncio"""
#     try:
#         loop = asyncio.get_event_loop()
#         if executor:
#             result = await loop.run_in_executor(executor, mp_q.get)
#         else:
#             with ThreadPoolExecutor(max_workers=1) as pool:
#                 result = await loop.run_in_executor(pool, mp_q.get)
#     except Exception as ex:
#         result = ex
#     return result
