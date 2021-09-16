import os
import dns.resolver


def resolve_url_custom_dns(hostname: str, nameservers: list = None):
    if nameservers is None:
        nameservers = ['8.8.8.8']
    my_resolver = dns.resolver.Resolver()

    # 8.8.8.8 is Google's public DNS server
    my_resolver.nameservers = nameservers

    try:
        answer = my_resolver.query(hostname)
        address = list(answer)[0].address
        return f"{address}:8000"
    except dns.resolver.NXDOMAIN:
        return None
