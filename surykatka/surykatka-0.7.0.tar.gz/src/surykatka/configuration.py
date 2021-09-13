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

import configparser
import os
from dns.resolver import get_default_resolver


CONFIG_SECTION = "SURYKATKA"


def createConfiguration(
    envvar="SURYKATKA_SETTINGS", cfgfile=None, mapping=None
):
    config = configparser.ConfigParser(empty_lines_in_values=False)
    # Default values
    config[CONFIG_SECTION] = {"INTERVAL": -1, "DOMAIN": "", "URL": ""}

    # User defined values
    if (envvar is not None) and (envvar in os.environ):
        config.read([os.environ.get(envvar)])
    if cfgfile is not None:
        config.read([cfgfile])
    if mapping is not None:
        config.read_dict({CONFIG_SECTION: mapping})

    # Required values
    if "SQLITE" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["SQLITE"] = ":memory:"
    if "NAMESERVER" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["NAMESERVER"] = "\n".join(
            get_default_resolver().nameservers
        )

    if "PUBLIC_SUFFIX" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["PUBLIC_SUFFIX"] = ""
    if "DOMAIN" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["DOMAIN"] = ""
    if "URL" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["URL"] = ""
    if "FORMAT" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["FORMAT"] = "json"
    if "WARNING_PERIOD" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["WARNING_PERIOD"] = str(60 * 60 * 24 * 7)
    if "TIMEOUT" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["TIMEOUT"] = "1"
    if "ELAPSED_FAST" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["ELAPSED_FAST"] = "0.2"
    if "ELAPSED_MODERATE" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["ELAPSED_MODERATE"] = "0.5"
    if "RELOAD" not in config[CONFIG_SECTION]:
        config[CONFIG_SECTION]["RELOAD"] = str(False)

    if config[CONFIG_SECTION]["SQLITE"] == ":memory:":
        # Do not loop when using temporary DB
        config[CONFIG_SECTION]["INTERVAL"] = "-1"

    return config[CONFIG_SECTION]


def logConfiguration(db, status_id, config):
    with db._db.atomic():
        for key, value in config.items():
            try:
                # Check previous parameter value
                previous_value = (
                    db.ConfigurationChange.select()
                    .where(db.ConfigurationChange.parameter == key)
                    .order_by(db.ConfigurationChange.status.desc())
                    .get()
                    .value
                )
            except db.ConfigurationChange.DoesNotExist:
                previous_value = None

            if previous_value != value:
                db.ConfigurationChange.create(
                    status=status_id, parameter=key, value=value
                )
