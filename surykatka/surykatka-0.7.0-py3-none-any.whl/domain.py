# Copyright (C) 2021  Nexedi SA and Contributors.
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

import sys
import os
import whois
from peewee import fn


def reportWhoisQuery(db, domain=None):
    query = (
        db.DomainChange.select(db.DomainChange)
        .group_by(db.DomainChange.domain)
        .having(db.DomainChange.status_id == fn.MAX(db.DomainChange.status_id))
    )

    if domain is not None:
        if type(domain) == list:
            query = query.where(db.DomainChange.domain << domain)
        else:
            query = query.where(db.DomainChange.domain == domain)
    return query


def packDomain(db):
    with db._db.atomic():
        result = [x for x in reportWhoisQuery(db)]
        for dns_change in result:
            db.DomainChange.delete().where(
                db.DomainChange.status_id != dns_change.status_id,
                db.DomainChange.domain == dns_change.domain,
            ).execute()


def logWhoisQuery(
    db,
    status_id,
    domain_text,
    registrar,
    whois_server,
    creation_date,
    updated_date,
    expiration_date,
    name_servers,
    whois_status,
    emails,
    dnssec,
    name,
    org,
    address,
    city,
    state,
    zipcode,
    country,
):

    with db._db.atomic():
        try:
            # Check previous parameter value
            previous_entry = reportWhoisQuery(db, domain=domain_text).get()
        except db.DomainChange.DoesNotExist:
            previous_entry = None

        if (
            (previous_entry is None)
            or (previous_entry.registrar != registrar)
            or (previous_entry.whois_server != whois_server)
            or (previous_entry.creation_date != creation_date)
            or (previous_entry.updated_date != updated_date)
            or (previous_entry.expiration_date != expiration_date)
            or (previous_entry.name_servers != name_servers)
            or (previous_entry.whois_status != whois_status)
            or (previous_entry.emails != emails)
            or (previous_entry.dnssec != dnssec)
            or (previous_entry.name != name)
            or (previous_entry.org != org)
            or (previous_entry.address != address)
            or (previous_entry.city != city)
            or (previous_entry.state != state)
            or (previous_entry.zipcode != zipcode)
            or (previous_entry.country != country)
        ):
            previous_entry = db.DomainChange.create(
                domain=domain_text,
                registrar=registrar,
                whois_server=whois_server,
                creation_date=creation_date,
                updated_date=updated_date,
                expiration_date=expiration_date,
                name_servers=name_servers,
                whois_status=whois_status,
                emails=emails,
                dnssec=dnssec,
                name=name,
                org=org,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                country=country,
                status=status_id,
            )

    return previous_entry.status_id


def queryWhois(db, status_id, domain_text):
    # Hide lib message:
    # Error trying to connect to socket: closing socket
    _stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    whois_dict = whois.whois(domain_text)
    sys.stdout = _stdout

    arg_list = []
    for arg in [
        whois_dict.registrar,
        whois_dict.whois_server,
        whois_dict.creation_date,
        whois_dict.updated_date,
        whois_dict.expiration_date,
        whois_dict.name_servers,
        whois_dict.status,
        whois_dict.emails,
        whois_dict.dnssec,
        whois_dict.name,
        whois_dict.org,
        whois_dict.address,
        whois_dict.city,
        whois_dict.state,
        whois_dict.zipcode,
        whois_dict.country,
    ]:
        if type(arg) == list:
            arg = arg[0]
        arg_list.append(arg)

    logWhoisQuery(db, status_id, domain_text, *arg_list)
    return whois_dict
