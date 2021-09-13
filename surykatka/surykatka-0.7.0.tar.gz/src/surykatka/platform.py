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

import miniupnpc
from dns.resolver import get_default_resolver
import platform
import socket


def checkPlatform(version):
    config = {
        "platform": platform.platform(),
        "python_build": platform.python_build(),
        "python_compiler": platform.python_compiler(),
        "python_branch": platform.python_branch(),
        "python_implementation": platform.python_implementation(),
        "python_revision": platform.python_revision(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
        "version": version,
    }

    config["resolvers"] = get_default_resolver().nameservers

    u = miniupnpc.UPnP()
    u.discoverdelay = 1000
    u.discover()
    try:
        u.selectigd()
        config["ip"] = u.externalipaddress()
    except Exception:
        config["ip"] = None
    return config


def logPlatform(db, version, status_id):
    config = checkPlatform(version)
    with db._db.atomic():
        for key, value in config.items():
            value = str(value)
            try:
                # Check previous parameter value
                previous_value = (
                    db.PlatformChange.select()
                    .where(db.PlatformChange.parameter == key)
                    .order_by(db.PlatformChange.status.desc())
                    .get()
                    .value
                )
            except db.PlatformChange.DoesNotExist:
                previous_value = None

            if previous_value != value:
                db.PlatformChange.create(
                    status=status_id, parameter=key, value=value
                )
