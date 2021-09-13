# Copyright 2009-2018 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""Custom authentication for the SSH server.

Launchpad's SSH server authenticates users against a XML-RPC service (see
`lp.services.authserver.interfaces.IAuthServer` and
`PublicKeyFromLaunchpadChecker`) and provides richer error messages in the
case of failed authentication (see `SSHUserAuthServer`).
"""

from __future__ import absolute_import, print_function

__metaclass__ = type
__all__ = [
    'LaunchpadAvatar',
    'PublicKeyFromLaunchpadChecker',
    'SSHUserAuthServer',
    ]

import base64
import binascii
import sys

from twisted.conch import avatar
from twisted.conch.error import (
    ConchError,
    ValidPublicKey,
    )
from twisted.conch.interfaces import IConchUser
from twisted.conch.ssh import (
    keys,
    userauth,
    )
from twisted.conch.ssh.common import (
    getNS,
    NS,
    )
from twisted.cred import credentials
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.logger import Logger
from twisted.python import failure
from twisted.web import xmlrpc
from zope.event import notify
from zope.interface import implementer

from lazr.sshserver import events
from lazr.sshserver.session import PatchedSSHSession
from lazr.sshserver.sftp import FileTransferServer


log = Logger()


# Private helper copied from twisted.python.compat.
def _bytesChr(i):
    """
    Like L{chr} but always works on ASCII, returning L{bytes}.

    @param i: The ASCII code point to return.
    @type i: L{int}

    @rtype: L{bytes}
    """
    if sys.version_info[0] >= 3:
        return bytes([i])
    else:
        return chr(i)


# The error_code value must be kept in sync with
# launchpad/lib/lp/xmlrpc/faults.py.  A test in the Launchpad tree ensures
# this.
class NoSuchPersonWithName(xmlrpc.Fault):
    """There's no Person with the specified name registered in Launchpad."""

    error_code = 200
    msg_template = 'No such person or team: %(person_name)s'

    def __init__(self, person_name):
        super(NoSuchPersonWithName, self).__init__(
            self.error_code, self.msg_template % {"person_name": person_name})


class LaunchpadAvatar(avatar.ConchUser):
    """An account on the SSH server, corresponding to a Launchpad person.

    :ivar channelLookup: See `avatar.ConchUser`.
    :ivar subsystemLookup: See `avatar.ConchUser`.
    :ivar user_id: The Launchpad database ID of the Person for this account.
    :ivar username: The Launchpad username for this account.
    """

    def __init__(self, user_dict):
        """Construct a `LaunchpadAvatar`.

        :param user_dict: The result of a call to
            `IAuthServer.getUserAndSSHKeys`.
        """
        avatar.ConchUser.__init__(self)
        self.user_id = user_dict['id']
        self.username = user_dict['name']

        # Set the only channel as a standard SSH session (with a couple of bug
        # fixes).
        self.channelLookup = {b'session': PatchedSSHSession}
        # ...and set the only subsystem to be SFTP.
        self.subsystemLookup = {b'sftp': FileTransferServer}

    def logout(self):
        notify(events.UserLoggedOut(self))


class UserDisplayedUnauthorizedLogin(UnauthorizedLogin):
    """UnauthorizedLogin which should be reported to the user."""


class ISSHPrivateKeyWithMind(credentials.ISSHPrivateKey):
    """Marker interface for SSH credentials that reference a Mind."""


@implementer(ISSHPrivateKeyWithMind)
class SSHPrivateKeyWithMind(credentials.SSHPrivateKey):
    """SSH credentials that also reference a Mind."""

    def __init__(self, username, algName, blob, sigData, signature, mind):
        credentials.SSHPrivateKey.__init__(
            self, username, algName, blob, sigData, signature)
        self.mind = mind


class UserDetailsMind:
    """A 'Mind' object that answers and caches requests for user details.

    A mind is a (poorly named) concept from twisted.cred that basically can be
    passed to portal.login to represent the client side view of
    authentication.  In our case we attach a mind to the SSHUserAuthServer
    object that corresponds to an attempt to authenticate against the server.
    """

    def __init__(self):
        self.cache = {}

    def lookupUserDetails(self, proxy, username):
        """Find details for the named user, including registered SSH keys.

        This method basically wraps `IAuthServer.getUserAndSSHKeys` -- see the
        documentation of that method for more details -- and caches the
        details found for any particular user.

        :param proxy: A twisted.web.xmlrpc.Proxy object for the authentication
            endpoint.
        :param username: The username to look up.
        """
        username = username.decode('UTF-8')
        if username in self.cache:
            return defer.succeed(self.cache[username])
        else:
            d = proxy.callRemote('getUserAndSSHKeys', username)
            d.addBoth(self._add_to_cache, username)
            return d

    def _add_to_cache(self, result, username):
        """Add the results to our cache."""
        self.cache[username] = result
        return result


class SSHUserAuthServer(userauth.SSHUserAuthServer):
    """Subclass of Conch's SSHUserAuthServer to customize various behaviours.

    There are two main differences:

     * We override ssh_USERAUTH_REQUEST to display as a banner the reason why
       an authentication attempt failed.

     * We override auth_publickey to create credentials that reference a
       UserDetailsMind and pass the same mind to self.portal.login.

    Conch is not written in a way to make this easy; we've had to copy and
    paste and change the implementations of these methods.
    """

    def __init__(self, transport=None, banner=None):
        self.transport = transport
        self._banner = banner
        self._configured_banner_sent = False
        self._mind = UserDetailsMind()
        self.interfaceToMethod = userauth.SSHUserAuthServer.interfaceToMethod
        self.interfaceToMethod[ISSHPrivateKeyWithMind] = b'publickey'

    def sendBanner(self, text, language='en'):
        bytes = b'\r\n'.join(text.encode('UTF8').splitlines() + [b''])
        self.transport.sendPacket(userauth.MSG_USERAUTH_BANNER,
                                  NS(bytes) + NS(language))

    def _sendConfiguredBanner(self, passed_through):
        if not self._configured_banner_sent and self._banner:
            self._configured_banner_sent = True
            self.sendBanner(self._banner)
        return passed_through

    def ssh_USERAUTH_REQUEST(self, packet):
        # This is copied and pasted from twisted/conch/ssh/userauth.py in
        # Twisted 8.0.1. We do this so we can add _ebLogToBanner between
        # two existing errbacks.
        user, nextService, method, rest = getNS(packet, 3)
        if user != self.user or nextService != self.nextService:
            self.authenticatedWith = []  # clear auth state
        self.user = user
        self.nextService = nextService
        self.method = method
        d = self.tryAuth(method, user, rest)
        if not d:
            self._ebBadAuth(failure.Failure(ConchError('auth returned none')))
            return
        d.addCallback(self._sendConfiguredBanner)
        d.addCallback(self._cbFinishedAuth)
        d.addErrback(self._ebMaybeBadAuth)
        # This line does not appear in the original.
        d.addErrback(self._ebLogToBanner)
        d.addErrback(self._ebBadAuth)
        return d

    def _cbFinishedAuth(self, result):
        ret = userauth.SSHUserAuthServer._cbFinishedAuth(self, result)
        # Tell the avatar about the transport, so we can tie it to the
        # connection in the logs.
        avatar = self.transport.avatar
        avatar.transport = self.transport
        notify(events.UserLoggedIn(avatar))
        return ret

    def _ebLogToBanner(self, reason):
        reason.trap(UserDisplayedUnauthorizedLogin)
        self.sendBanner(reason.getErrorMessage())
        return reason

    def getMind(self):
        """Return the mind that should be passed to self.portal.login().

        If multiple requests to authenticate within this overall login attempt
        should share state, this method can return the same mind each time.
        """
        return self._mind

    def makePublicKeyCredentials(self, username, algName, blob, sigData,
                                 signature):
        """Construct credentials for a request to login with a public key.

        Our implementation returns a SSHPrivateKeyWithMind.

        :param username: The username the request is for.
        :param algName: The algorithm name for the blob.
        :param blob: The public key blob as sent by the client.
        :param sigData: The data the signature was made from.
        :param signature: The signed data.  This is checked to verify that the
            user owns the private key.
        """
        mind = self.getMind()
        return SSHPrivateKeyWithMind(
                username, algName, blob, sigData, signature, mind)

    def auth_publickey(self, packet):
        # This is copied and pasted from twisted/conch/ssh/userauth.py in
        # Twisted 8.0.1. We do this so we can customize how the credentials
        # are built and pass a mind to self.portal.login.
        hasSig = ord(packet[0:1])
        algName, blob, rest = getNS(packet[1:], 2)
        try:
            pubKey = keys.Key.fromString(blob)
        except Exception as e:
            return defer.fail(UnauthorizedLogin(str(e)))
        signature = hasSig and getNS(rest)[0] or None
        if hasSig:
            # Work around a bug in paramiko < 2.0.0: if the most significant
            # byte of an RSA signature is zero, then it strips leading zero
            # bytes rather than zero-padding it to the correct length.
            if algName == b'ssh-rsa':
                signatureType, rawSignature, rest = getNS(signature, 2)
                pubKeyLen = (pubKey.size() + 7) // 8
                if len(rawSignature) < pubKeyLen:
                    rawSignature = (
                        b'\x00' * (pubKeyLen - len(rawSignature)) +
                        rawSignature)
                    signature = NS(signatureType) + NS(rawSignature) + rest
            b = (
                NS(self.transport.sessionID) +
                _bytesChr(userauth.MSG_USERAUTH_REQUEST) + NS(self.user) +
                NS(self.nextService) + NS(b'publickey') +
                _bytesChr(hasSig) + NS(pubKey.sshType()) + NS(blob))
            # The next three lines are different from the original.
            c = self.makePublicKeyCredentials(
                self.user, algName, blob, b, signature)
            return self.portal.login(c, self.getMind(), IConchUser)
        else:
            # The next four lines are different from the original.
            c = self.makePublicKeyCredentials(
                self.user, algName, blob, None, None)
            return self.portal.login(
                c, self.getMind(), IConchUser).addErrback(
                    self._ebCheckKey, packet[1:])


# XXX cjwatson 2019-10-18: Ideally we'd use
# twisted.conch.checkers.SSHPublicKeyChecker rather than cloning-and-hacking
# it.  Unfortunately the IAuthorizedKeysDB interface doesn't allow
# getAuthorizedKeys to return a Deferred, so we have no way to do
# asynchronous work there such as talking to the authserver.
@implementer(ICredentialsChecker)
class PublicKeyFromLaunchpadChecker:
    """Cred checker for getting public keys from launchpad.

    It knows how to get the public keys from the authserver.
    """
    credentialInterfaces = (ISSHPrivateKeyWithMind,)

    def __init__(self, authserver):
        self.authserver = authserver

    def requestAvatarId(self, credentials):
        """See `ICredentialsChecker`."""
        d = defer.maybeDeferred(self._checkKey, credentials)
        d.addCallback(self._verifyKey, credentials)
        return d

    def _checkKey(self, credentials):
        """Check whether `credentials` is a valid request to authenticate.

        We check the key data in credentials against the keys the named user
        has registered in Launchpad.
        """
        try:
            username = credentials.username.decode('UTF-8')
        except UnicodeDecodeError:
            # Launchpad account names must be valid UTF-8.
            return defer.fail(UserDisplayedUnauthorizedLogin(
                "No such Launchpad account: %r" % credentials.username))
        d = credentials.mind.lookupUserDetails(
            self.authserver, credentials.username)
        d.addCallback(self._checkForAuthorizedKey, credentials)
        d.addErrback(self._reportNoSuchUser, username)
        return d

    def _reportNoSuchUser(self, failure, username):
        """Report that the given username does not exist."""
        failure.trap(xmlrpc.Fault)
        fault = failure.value
        if fault.faultCode == NoSuchPersonWithName.error_code:
            raise UserDisplayedUnauthorizedLogin(
                "No such Launchpad account: %s" % username)
        raise failure

    def _checkForAuthorizedKey(self, user_dict, credentials):
        """Check the key data in credentials against the keys found in LP."""
        if credentials.algName == b'ssh-dss':
            wantKeyType = 'DSA'
        elif credentials.algName == b'ssh-rsa':
            wantKeyType = 'RSA'
        elif credentials.algName.startswith(b'ecdsa-sha2-'):
            wantKeyType = 'ECDSA'
        elif credentials.algName == b'ssh-ed25519':
            wantKeyType = 'ED25519'
        else:
            # unknown key type
            return False

        if len(user_dict['keys']) == 0:
            raise UserDisplayedUnauthorizedLogin(
                "Launchpad user '%s' doesn't have a registered SSH key"
                % user_dict['name'])

        for keytype, keytext in user_dict['keys']:
            if keytype != wantKeyType:
                continue
            try:
                if base64.b64decode(keytext) == credentials.blob:
                    return True
            except binascii.Error:
                continue

        raise UnauthorizedLogin(
            "Your SSH key does not match any key registered for Launchpad "
            "user %s" % user_dict['name'])

    def _verifyKey(self, validKey, credentials):
        """Check whether the credentials themselves are valid.

        By this point, we know that the key matches the user.
        """
        if not validKey:
            raise UnauthorizedLogin("invalid key")
        if not credentials.signature:
            raise ValidPublicKey()
        try:
            pubKey = keys.Key.fromString(credentials.blob)
            if pubKey.verify(credentials.signature, credentials.sigData):
                return credentials.username
        except Exception:  # Any error should be treated as a failed login
            log.failure("Error while verifying key")
            raise UnauthorizedLogin("Error while verifying key")

        raise UnauthorizedLogin("Key signature invalid.")
