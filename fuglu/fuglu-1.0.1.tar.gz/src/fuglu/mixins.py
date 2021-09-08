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
#

import time
import typing as tp
from typing import Dict, Optional
from configparser import RawConfigParser, _UNSET


class ConfigWrapper(object):
    """Wrap a RawConfigParser object defining default values by a dict"""
    def __init__(self, config: RawConfigParser, defaultdict: Optional[Dict] = None):
        self._config = config
        self._defaultdict = defaultdict

    def _get_fallback(self, option, **kwargs):
        """Extract fallback argument from parameters, set fallback from defaults"""
        if 'fallback' in kwargs:
            fallback = kwargs.pop('fallback')
        else:
            try:
                fallback = self._defaultdict[option]['default']
            except KeyError:
                fallback = _UNSET
        return fallback

    def get(self, section: str, option: str, fallback=_UNSET, **kwargs):
        """
        Wraps RawConfigParser.get with default fallback from internal
        class dictionary.
        """
        if fallback == _UNSET:
            fallback = self._get_fallback(option, **kwargs)
        return self._config.get(section, option, fallback=fallback, **kwargs)

    def getint(self, section: str, option: str, fallback=_UNSET, **kwargs):
        """
        Wraps RawConfigParser.getint with default fallback from internal
        class dictionary.
        """
        if fallback == _UNSET:
            fallback = self._get_fallback(option, **kwargs)
            if isinstance(fallback, str):
                # convert using RawConfigParser method which just uses 'int'
                fallback = int(fallback)
        return self._config.getint(section, option, fallback=fallback, **kwargs)

    def getfloat(self, section: str, option: str, fallback=_UNSET, **kwargs):
        """
        Wraps RawConfigParser.getfloat with default fallback from internal
        class dictionary.
        """
        if fallback == _UNSET:
            fallback = self._get_fallback(option, **kwargs)
            if isinstance(fallback, str):
                # convert using RawConfigParser method which just uses 'float'
                fallback = float(fallback)
        return self._config.getfloat(section, option, fallback=fallback, **kwargs)

    def getboolean(self, section: str, option: str, fallback=_UNSET, **kwargs):
        """
        Wraps RawConfigParser.getboolean with default fallback from internal
        class dictionary.
        """
        if fallback == _UNSET:
            fallback = self._get_fallback(option, **kwargs)
            if isinstance(fallback, str):
                # convert using RawConfigParser method
                fallback = self._config._convert_to_boolean(fallback)

        return self._config.getboolean(section, option, fallback=fallback, **kwargs)
    
    def getlist(self, section: str, option: str, fallback=_UNSET, **kwargs):
        """
        Wraps FuConfigParser.getlist with default fallback from internal
        class dictionary.
        """
        #from .shared import FuConfigParser
        #self._config: FuConfigParser
        if fallback == _UNSET:
            fallback = self._get_fallback(option, **kwargs)
        return self._config.getlist(section, option, fallback=fallback, **kwargs)

    def __getattr__(self, name):
        """
        Delegate to RawConfigParser.
        """
        return getattr(self._config, name)


class DefConfigMixin(object):
    def __init__(self, config):
        self._config = ConfigWrapper(config, None)
        self._rawconfig = config

    @property
    def config(self):
        try:
            if self._config._defaultdict is not self.requiredvars:
                self._config._defaultdict = self.requiredvars
        except AttributeError:
            pass
        return self._config

    @config.setter
    def config(self, newconfig: RawConfigParser):
        if self._rawconfig is not newconfig:
            self._config = ConfigWrapper(newconfig, None)


class SimpleTimeoutMixin(object):
    """Simple timeout mixin for given tags"""
    def __init__(self):
        self._stimedict = {}
        self._stimehit = {}

    def stimeout_set_timer(self, name: str, timeout: float):
        if timeout:
            now = time.time()
            self._stimedict[name] = (now + timeout, now, timeout)

    def stimeout_continue(self, name: str):
        timeout_end, timeout_start, timeout_duration = self._stimedict.get(name, (0, 0, 0))
        if timeout_end and time.time() > timeout_end:
            self._stimehit[name] = True
            return False
        else:
            return True

    def stimeout_string(self, name: str):
        timeout_end, timeout_start, timeout_duration = self._stimedict.get(name, (0, 0, 0))
        if timeout_duration:
            return f"timeout(real/limit) = {(time.time()-timeout_start):.1f}/{timeout_duration:.1f} [s]"
        else:
            return "no timeout"


class ReturnOverrideMixin(object):
    def __init__(self, config, section: tp.Optional[str] = None):
        super().__init__(config, section=section)
        self._overrideaction = -1
        self._milt_overrideaction = b"undefined"
        self._overridemessage = None

    @property
    def overrideaction(self):
        """get override-action which will be returned instead of 'real' plugin output"""
        if isinstance(self._overrideaction, int) and self._overrideaction < 0:
            # setup return code override if given in config
            self._overrideaction = None
            try:
                overrideaction = self.config.get(self.section, 'overrideaction')
            except Exception:
                overrideaction = None
            try:
                overridemessage = self.config.get(self.section, 'overridemessage')
                overridemessage = overridemessage.strip()
            except Exception:
                overridemessage = None

            if overrideaction:
                from fuglu.shared import string_to_actioncode
                # import here to prevent circular dependency
                self._overrideaction = string_to_actioncode(overrideaction, self.config)
            if overridemessage:
                self._overridemessage = overridemessage
        return self._overrideaction

    @property
    def milter_overrideaction(self):
        if isinstance(self._milt_overrideaction, bytes) and self._milt_overrideaction == b"undefined":
            self._milt_overrideaction = None
            from fuglu.mshared import retcode2milter
            if self.overrideaction is not None:
                self._milt_overrideaction = retcode2milter.get(self.overrideaction)
        return self._milt_overrideaction

    def _check_apply_override(self,
                              out: tp.Optional[tp.Union[int, tp.Tuple[int, str]]] = None,
                              suspectid: str = "<>") -> tp.Optional[tp.Union[int, tp.Tuple[int, str]]]:
        """Run examine method of plugin + additional pre/post calculations"""

        from fuglu.shared import actioncode_to_string
        # import here to prevent circular dependency

        if isinstance(out, tuple):
            ret, msg = out
        else:
            ret = out
            msg = None

        if self.overrideaction is not None:
            if ret is not None and ret != self.overrideaction:
                plugin_return = actioncode_to_string(ret)
                plugin_msg = msg if msg else ""
                override_return = actioncode_to_string(self.overrideaction)
                override_msg = self._overridemessage if self._overridemessage else ""
                self._logger().warning(f"{suspectid} overrideaction: "
                                       f"plugin={plugin_return}/msg={plugin_msg}, "
                                       f"override={override_return}/msg={override_msg}")
                ret = self.overrideaction
                msg = self._overridemessage

        if msg is not None:
            return ret, msg
        else:
            return ret

    def _check_apply_override_milter(self,
                                     out: tp.Optional[tp.Union[int, tp.Tuple[int, str]]] = None,
                                     suspectid: str = "<>") -> tp.Union[bytes, tp.Tuple[bytes, str]]:

        from fuglu.connectors.milterconnector import RETCODE2STR
        # import here to prevent circular dependency

        if isinstance(out, tuple):
            ret, msg = out
        else:
            ret = out
            msg = None

        if self.milter_overrideaction is not None:
            if ret is not None and ret != self.milter_overrideaction:
                plugin_return = RETCODE2STR.get(ret)
                plugin_msg = msg if msg else ""
                override_return = RETCODE2STR.get(self.milter_overrideaction)
                override_msg = self._overridemessage if self._overridemessage else ""
                self._logger().warning(f"{suspectid} overrideaction: "
                                       f"plugin={plugin_return}/msg={plugin_msg}, "
                                       f"override={override_return}/msg={override_msg}")
                ret = self.milter_overrideaction
                msg = self._overridemessage

        if msg is not None:
            return ret, msg
        else:
            return ret
