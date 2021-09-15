from opps_sdk.opps_client import OppsClient
from opps_sdk.core.rsa_utils import rsa_long_encrypt


class Cert(object):
    """
    证件
    """
    cert_type = ""  # 证件类型
    cert_id = ""  # 证件ID
    cert_validity_type = ""  # 个人证件有效期类型
    cert_begin_date = ""  # 个人证件有效期起始日
    cert_end_date = ""  # 个人证件有效期到期日，长期有效不填

    def __init__(self, cert_type, cert_id, cert_validity_type, cert_begin_date, cert_end_date=""):
        self.cert_type = cert_type
        self.cert_id = rsa_long_encrypt(cert_id, OppsClient.mer_config.public_key)
        self.cert_validity_type = cert_validity_type
        self.cert_begin_date = cert_begin_date
        self.cert_end_date = cert_end_date
