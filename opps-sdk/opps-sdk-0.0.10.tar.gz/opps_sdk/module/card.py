from opps_sdk.opps_client import OppsClient
from opps_sdk.core.rsa_utils import rsa_long_encrypt


class Card(object):
    """
    证件
    """
    card_id = ""  # 卡号
    card_name = ""  # 卡姓名
    card_mp = ""  # 个人证件有效期类型
    vip_code = ""  # 个人证件有效期起始日
    expiration = ""  # 个人证件有效期到期日，长期有效不填

    def __init__(self, card_id, card_name, card_mp, vip_code="", expiration=""):
        self.card_id = rsa_long_encrypt(card_id, OppsClient.mer_config.public_key)
        self.card_name = rsa_long_encrypt(card_name, OppsClient.mer_config.public_key)
        self.card_mp = rsa_long_encrypt(card_mp, OppsClient.mer_config.public_key)
        self.vip_code = rsa_long_encrypt(vip_code, OppsClient.mer_config.public_key)
        self.expiration = rsa_long_encrypt(expiration, OppsClient.mer_config.public_key)
