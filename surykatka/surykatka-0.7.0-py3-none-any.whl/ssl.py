# Copyright (C) 2019  Nexedi SA and Contributors.
#                     Romain Courteaud <romain@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.

from peewee import fn
import socket
import ssl
import hashlib
from binascii import hexlify
import datetime


TIMEOUT = 2


def reportSslCertificate(db, ip=None, port=None, hostname=None):
    query = (
        db.SslChange.select(db.SslChange)
        .group_by(db.SslChange.ip, db.SslChange.port, db.SslChange.hostname,)
        .having(db.SslChange.status_id == fn.MAX(db.SslChange.status_id))
    )

    if hostname is not None:
        if type(hostname) == list:
            query = query.where(db.SslChange.hostname << hostname)
        else:
            query = query.where(db.SslChange.hostname == hostname)
    if port is not None:
        if type(port) == list:
            query = query.where(db.SslChange.port << port)
        else:
            query = query.where(db.SslChange.port == port)
    if ip is not None:
        if type(ip) == list:
            query = query.where(db.SslChange.ip << ip)
        else:
            query = query.where(db.SslChange.ip == ip)
    return query


def packSslCertificate(db):
    with db._db.atomic():
        result = [x for x in reportSslCertificate(db)]
        for ssl_change in result:
            db.SslChange.delete().where(
                db.SslChange.status_id != ssl_change.status_id,
                db.SslChange.hostname == ssl_change.hostname,
                db.SslChange.port == ssl_change.port,
                db.SslChange.ip == ssl_change.ip,
            ).execute()


def logSslCertificate(
    db,
    ip,
    port,
    hostname,
    sha1_fingerprint,
    not_before,
    not_after,
    subject,
    issuer,
    status_id,
):

    with db._db.atomic():
        try:
            # Check previous parameter value
            previous_entry = reportSslCertificate(
                db, ip=ip, port=port, hostname=hostname
            ).get()
        except db.SslChange.DoesNotExist:
            previous_entry = None

        if (previous_entry is None) or (
            previous_entry.sha1_fingerprint != sha1_fingerprint
        ):
            previous_entry = db.SslChange.create(
                status=status_id,
                ip=ip,
                port=port,
                hostname=hostname,
                sha1_fingerprint=sha1_fingerprint,
                not_before=not_before,
                not_after=not_after,
                subject=subject,
                issuer=issuer,
            )
        return previous_entry.status_id


def hasValidSSLCertificate(db, ip, port, hostname, status_id, timeout=TIMEOUT):
    ssl_context = ssl.create_default_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    wrapped_sock = ssl_context.wrap_socket(sock, server_hostname=hostname)

    try:
        wrapped_sock.connect((ip, port))
        der = wrapped_sock.getpeercert(True)
        # XXX How to extract info from the der directly?
        ssl_info = wrapped_sock.getpeercert()

    except (ssl.SSLError, ConnectionRefusedError, socket.timeout, OSError):
        wrapped_sock.close()
        # XXX Expired certificate can not be fetched with the builtin ssl lib
        # pyOpenSSL is one way to fix this
        # https://stackoverflow.com/a/52298575
        logSslCertificate(
            db, ip, port, hostname, None, None, None, None, None, status_id,
        )
        return False
    except:
        wrapped_sock.close()
        raise

    wrapped_sock.close()

    sha1_fingerprint = hexlify(hashlib.sha1(der).digest())
    ssl_date_fmt = "%b %d %H:%M:%S %Y %Z"
    not_before = datetime.datetime.strptime(
        ssl_info["notBefore"], ssl_date_fmt
    )
    not_after = datetime.datetime.strptime(ssl_info["notAfter"], ssl_date_fmt)
    subject = dict([y for x in ssl_info["subject"] for y in x]).get(
        "commonName", ""
    )
    issuer = dict([y for x in ssl_info["issuer"] for y in x]).get(
        "commonName", ""
    )
    logSslCertificate(
        db,
        ip,
        port,
        hostname,
        sha1_fingerprint.decode(),
        not_before,
        not_after,
        subject,
        issuer,
        status_id,
    )
    return True
