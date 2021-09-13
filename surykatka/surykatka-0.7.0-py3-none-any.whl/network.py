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

import socket
import errno
from peewee import fn


TIMEOUT = 2


def reportNetwork(db, ip=None, transport=None, port=None):
    query = (
        db.NetworkChange.select(db.NetworkChange)
        .group_by(
            db.NetworkChange.ip,
            db.NetworkChange.transport,
            db.NetworkChange.port,
        )
        .having(
            db.NetworkChange.status_id == fn.MAX(db.NetworkChange.status_id)
        )
    )

    if transport is not None:
        if type(transport) == list:
            query = query.where(db.NetworkChange.transport << transport)
        else:
            query = query.where(db.NetworkChange.transport == transport)
    if port is not None:
        if type(port) == list:
            query = query.where(db.NetworkChange.port << port)
        else:
            query = query.where(db.NetworkChange.port == port)
    if ip is not None:
        if type(ip) == list:
            query = query.where(db.NetworkChange.ip << ip)
        else:
            query = query.where(db.NetworkChange.ip == ip)
    return query


def packNetwork(db):
    with db._db.atomic():
        result = [x for x in reportNetwork(db)]
        for network_change in result:
            db.NetworkChange.delete().where(
                db.NetworkChange.status_id != network_change.status_id,
                db.NetworkChange.transport == network_change.transport,
                db.NetworkChange.port == network_change.port,
                db.NetworkChange.ip == network_change.ip,
            ).execute()


def logNetwork(db, ip, transport, port, state, status_id):

    with db._db.atomic():
        try:
            # Check previous parameter value
            previous_entry = reportNetwork(
                db, ip=ip, transport=transport, port=port
            ).get()
        except db.NetworkChange.DoesNotExist:
            previous_entry = None

        if (previous_entry is None) or (previous_entry.state != state):
            previous_entry = db.NetworkChange.create(
                status=status_id,
                ip=ip,
                transport=transport,
                port=port,
                state=state,
            )
        return previous_entry.status_id


def isTcpPortOpen(db, ip, port, status_id, timeout=TIMEOUT):
    is_open = False
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
        state = "open"
        is_open = True
    except ConnectionRefusedError:
        state = "closed"
    except (socket.timeout, TimeoutError):
        state = "filtered"
    except OSError as e:
        if e.errno == errno.EHOSTUNREACH:
            # OSError: [Errno 113] No route to host
            state = "filtered"
        elif e.errno == errno.ENETUNREACH:
            # OSError: [Errno 101] Network is unreachable
            state = "unreachable"
        else:
            sock.close()
            raise
    except:
        sock.close()
        raise

    sock.close()

    logNetwork(db, ip, "TCP", port, state, status_id)
    return is_open
