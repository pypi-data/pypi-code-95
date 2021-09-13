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

import dns
from .network import logNetwork
from peewee import fn

URL_TO_CHECK = "example.org"
TIMEOUT = 2


def reportDnsQuery(db, resolver_ip=None, domain=None, rdtype=None):
    query = (
        db.DnsChange.select(db.DnsChange)
        .group_by(
            db.DnsChange.resolver_ip, db.DnsChange.domain, db.DnsChange.rdtype
        )
        .having(db.DnsChange.status_id == fn.MAX(db.DnsChange.status_id))
    )

    if resolver_ip is not None:
        if type(resolver_ip) == list:
            query = query.where(db.DnsChange.resolver_ip << resolver_ip)
        else:
            query = query.where(db.DnsChange.resolver_ip == resolver_ip)
    if domain is not None:
        if type(domain) == list:
            query = query.where(db.DnsChange.domain << domain)
        else:
            query = query.where(db.DnsChange.domain == domain)
    if rdtype is not None:
        if type(rdtype) == list:
            query = query.where(db.DnsChange.rdtype << rdtype)
        else:
            query = query.where(db.DnsChange.rdtype == rdtype)
    return query


def packDns(db):
    with db._db.atomic():
        result = [x for x in reportDnsQuery(db)]
        for dns_change in result:
            db.DnsChange.delete().where(
                db.DnsChange.status_id != dns_change.status_id,
                db.DnsChange.resolver_ip == dns_change.resolver_ip,
                db.DnsChange.domain == dns_change.domain,
                db.DnsChange.rdtype == dns_change.rdtype,
            ).execute()


def logDnsQuery(db, status_id, resolver_ip, domain_text, rdtype, answer_list):
    answer_list.sort()
    response = ", ".join(answer_list)

    with db._db.atomic():
        try:
            # Check previous parameter value
            previous_entry = reportDnsQuery(
                db, resolver_ip=resolver_ip, domain=domain_text, rdtype=rdtype
            ).get()
        except db.DnsChange.DoesNotExist:
            previous_entry = None

        if (previous_entry is None) or (previous_entry.response != response):
            previous_entry = db.DnsChange.create(
                resolver_ip=resolver_ip,
                domain=domain_text,
                rdtype=rdtype,
                response=response,
                status=status_id,
            )

    return previous_entry.status_id


def buildResolver(resolver_ip, timeout):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers.append(resolver_ip)
    resolver.timeout = timeout
    resolver.lifetime = timeout
    resolver.edns = -1
    return resolver


def queryDNS(db, status_id, resolver_ip, domain_text, rdtype, timeout=TIMEOUT):
    # only A (and AAAA) has address property
    assert rdtype == "A"

    resolver = buildResolver(resolver_ip, timeout)
    try:
        answer_list = [
            x.address
            for x in resolver.query(
                domain_text, rdtype, raise_on_no_answer=False
            )
        ]
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.exception.Timeout,
        dns.resolver.NoNameservers,
    ):
        answer_list = []

    logDnsQuery(db, status_id, resolver_ip, domain_text, rdtype, answer_list)
    return answer_list


def getReachableResolverList(db, status_id, resolver_ip_list, timeout=TIMEOUT):
    # Create a list of resolver object
    result_ip_list = []
    # Check the DNS server availability once
    # to prevent using it later if it is down
    for resolver_ip in resolver_ip_list:
        resolver_state = "open"
        answer_list = queryDNS(
            db, status_id, resolver_ip, URL_TO_CHECK, "A", timeout
        )

        if len(answer_list) == 0:
            # We expect a valid response
            # Drop the DNS server...
            resolver_state = "closed"
        else:
            resolver_state = "open"
            result_ip_list.append(resolver_ip)
        logNetwork(db, resolver_ip, "UDP", 53, resolver_state, status_id)

    return result_ip_list


def expandDomainList(domain_list, public_suffix_list=None):
    for domain_text in domain_list:

        dns_name = dns.name.from_text(domain_text)
        if (len(dns_name.labels) - 1) > 2:
            # https://publicsuffix.org/list/public_suffix_list.dat
            parent_domain_text = dns_name.parent().to_text(omit_final_dot=True)
            if (public_suffix_list is None) or (
                parent_domain_text not in public_suffix_list
            ):
                domain_list.append(parent_domain_text)

    domain_list = list(set(domain_list))
    domain_list.sort()
    return domain_list


def getDomainIpDict(
    db, status_id, resolver_ip_list, domain_list, rdtype, timeout=TIMEOUT
):
    server_ip_dict = {}
    for domain_text in domain_list:
        for resolver_ip in resolver_ip_list:
            answer_list = queryDNS(
                db, status_id, resolver_ip, domain_text, rdtype, timeout
            )
            for address in answer_list:
                if address not in server_ip_dict:
                    server_ip_dict[address] = []
                if domain_text not in server_ip_dict[address]:
                    # Do not duplicate the domain
                    server_ip_dict[address].append(domain_text)
    return server_ip_dict
