from OpenSSL import crypto
from OpenSSL.crypto import PKey, X509
from typing import Tuple


def create_dns_str(dns=""):
    # type: (str) -> [str]
    """
    Creates a Subject Alternative Name formatted string from a comma-separated string
    :return: comma-separated SAN formatted string
    """
    separator = ","
    formatted_dns = []
    for d in dns.split(separator):
        formatted_dns.append("DNS:" + d)
    return (separator + " ").join(formatted_dns)


def create_cert(country="US", state="Colorado", location="Lousville", company="Swimlane Inc", application="swimlane.io", dns="*.swimlane.io"):
    # type: (str, str, str, str, str, str) -> Tuple[X509, PKey]
    """
    Creates default self generated cert and key.
    :return: Tuple with cert and key
    """
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    cert = crypto.X509()
    # this is actually X509v3, zero-based
    cert.set_version(2)
    cert.get_subject().C = country
    cert.get_subject().ST = state
    cert.get_subject().L = location
    cert.get_subject().OU = company
    cert.get_subject().CN = application
    cert.set_serial_number(1000)

    # validity period must be 825 days or fewer
    # https://support.apple.com/en-us/HT210176
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(824 * 24 * 60 * 60)

    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)

    # must contain subject alternative names with user provided dns entries
    # must contain EKU with id-kp-serverAuth OID
    # https://support.apple.com/en-us/HT210176
    formatted_dns = create_dns_str(dns)
    cert.add_extensions([
        crypto.X509Extension(b"subjectAltName", critical=True, value=formatted_dns.encode()),
        crypto.X509Extension(b"extendedKeyUsage", True, b"serverAuth")
    ])

    # must be SHA2+
    # https://support.apple.com/en-us/HT210176
    cert.sign(k, 'sha256')
    return cert, k
