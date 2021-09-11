import logging

import dns.resolver


def set_host_from_kubernetes_dns(host, host_fqdn):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['10.96.0.10'] # 쿠버 IP는 고정
    answers = resolver.resolve(host_fqdn, "A")
    ip = answers[0].to_text()
    record = "{} {}\n".format(ip, host)

    path = '/etc/hosts'
    lines = open(path, 'r').readlines()

    found = False
    changed = False

    for i, v in enumerate(lines):
        if host in v:
            found = True
            if v.split(' ')[0] != ip:
                lines[i] = record
                changed = True
            break

    if changed or not found:
        if not found:
            lines.append(record)
            logging.info("New record : {}".format(host))
        out = open(path, 'w')
        out.writelines(lines)
        out.close()
        logging.info("Synced record : {}".format(host))
