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
import re
import logging


# Singleton implementation for Addrcheck
class Addrcheck(object):
    """
    Singleton implementation for Addrcheck. Note it is important not
    to initialise "self._method" by creating a "__init__" function
    since this would be called whenever asking for the singleton...
    (Addrcheck() would call __init__).
    """
    __instance = None

    def __new__(cls):
        """
        Returns Singleton of Addrcheck (create if not yet existing)

        Returns:
            (Addrcheck) The singleton of Addrcheck
        """
        if Addrcheck.__instance is None:
            Addrcheck.__instance = object.__new__(cls)
            Addrcheck.__instance.set("Default")
        return Addrcheck.__instance

    def set(self, name):
        """
        Sets method to be used in valid - function to validate an address
        Args:
            name (String): String with name of validator
        """
        if name == "Default":
            self._method = Default()
        elif name == "LazyLocalPart":
            self._method = LazyLocalPart()
        elif name == "NoCheck":
            self._method = NoCheck()
        elif name == "AsciiOnly":
            self._method = AsciiOnly()
        else:
            logger = logging.getLogger("%s.Addrcheck" % __package__)
            logger.warning("Mail address check \"%s\" not valid, using default..."%name)
            self._method = Default()

    def valid(self, address: str, allow_postmaster: bool = False):
        """

        Args:
            address (String): Address to be checked
            allow_postmaster (Bool):

        Returns:
            (Boolean) True if address is valid using internal validation method

        """
        if allow_postmaster and address and address.lower() == "postmaster":
            # According to RFC5321 (https://tools.ietf.org/html/rfc5321#section-4.1.1.3)
            # postmaster is allowed as recipient without domain
            return True

        return self._method(address)


class Addrcheckint(object):
    """
    Functor interface for method called by Addrcheck
    """
    def __init__(self):
        pass
    def __call__(self, mailAddress):
        raise NotImplemented


class Default(Addrcheckint):
    """
    Default implementation (and backward compatible) which does not allow more than one '@'
    """
    def __init__(self):
        super(Default, self).__init__()
    def __call__(self,mailAddress):
        leg =  (mailAddress !='' and  (   re.match(r"[^@]+@[^@]+$", mailAddress)))
        return leg


class LazyLocalPart(Addrcheckint):
    """
    Allows '@' in local part if quoted
    """
    def __init__(self):
        super(LazyLocalPart, self).__init__()
    def __call__(self,mailAddress):
        leg = ( mailAddress !='' and  (      re.match(r"[^@]+@[^@]+$", mailAddress)
                                          or re.match(r"^\"[\x00-\x7f]+\"@[^@]+$", mailAddress) ))
        return leg


class AsciiOnly(Addrcheckint):
    """
    Allow ascii characters only, "@" in local part has to be quoted
    """
    def __init__(self):
        super().__init__()
        self.ascii_noadd = re.compile(r"^[\x00-\x3f\x41-\x7f]+@[\x00-\x3f\x41-\x7f]+$", flags=re.IGNORECASE)
        self.ascii_quoted = re.compile(r"^\"[\x00-\x7f]+\"@[\x00-\x3f\x41-\x7f]+$", flags=re.IGNORECASE)

    def __call__(self, mailAddress):
        # there has to be an "@" in the address
        return mailAddress and \
               (self.ascii_noadd.match(mailAddress) or self.ascii_quoted.match(mailAddress))


class NoCheck(Addrcheckint):
    """
    Disable check
    """
    def __init__(self):
        super(NoCheck, self).__init__()
    def __call__(self,mailAddress):
        return True
