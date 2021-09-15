from opps_sdk.core.rsa_utils import rsa_design, rsa_long_encrypt
from opps_sdk.module.request_tools import union_user_id, request_post
from opps_sdk.opps_client import OppsClient


class OppsTools(object):

    @classmethod
    def verify_sign(cls, data, sign, pub_key=""):
        """
        校验返回报文签名
        :param data: 返回data
        :param sign:  返回签名
        :param pub_key: 公钥，默认使用SDK初始化时的公钥
        :return: 是否通过校验
        """
        if not pub_key:
            pub_key = OppsClient.mer_config.public_key
        return rsa_design(sign, data, pub_key)

    @classmethod
    def union_user_id(cls, huifu_id, user_auth_code, **kwargs):
        """
        获取银联用户标识
        :param huifu_id:商户号
        :param user_auth_code:用户授权码
        :param kwargs:额外参数
        :return: 银联用户标识
        """
        required_params = {
            "huifu_id": huifu_id,
            "user_auth_code": user_auth_code,
        }

        if not kwargs.get("app_up_identifier"):
            kwargs["app_up_identifier"] = "CloudPay"

        required_params.update(kwargs)
        return request_post(union_user_id, required_params)

    @classmethod
    def encrypt_with_public_key(cls, orignal_str, public_key=""):
        """
        通过RSA 公钥加密敏感信息
        :param orignal_str: 原始字符串
        :param public_key: 公钥，不传使用商户配置公钥
        :return: 密文
        """
        if not public_key:
            public_key = OppsClient.mer_config.public_key
        return rsa_long_encrypt(orignal_str, public_key)
