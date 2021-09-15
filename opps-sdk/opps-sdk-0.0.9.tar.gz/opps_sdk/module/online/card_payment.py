from opps_sdk.module.request_tools import request_post, offline_payment_create, offline_payment_close, \
    offline_payment_query, offline_payment_refund, offline_payment_refund_query, offline_payment_scan, \
    request_post_without_seq_id
from opps_sdk.common_util import generate_mer_order_id, generate_req_date
from opps_sdk.opps_client import OppsClient
from opps_sdk.module.card import Card
from opps_sdk.module.cert import Cert


class CardPayment(object):
    """
    线上支付类，快捷支付相关接口，支付，退款，交易查询等
    """

    @classmethod
    def bind(cls, huifu_id, merch_name, out_cust_id, card_info: Card, cert_info: Cert, **kwargs):
        """
        快捷/代扣绑卡申请接口
        :param huifu_id:汇付Id
        :param merch_name:商户名称
        :param out_cust_id:顾客用户号
        :param card_info:银行卡信息
        :param cert_info:证件信息
        :param kwargs: 额外参数
        :return: 绑卡接口返回
        """
        required_params = {
            "huifu_id": huifu_id,
            "merch_name": merch_name,
            "out_cust_id": out_cust_id,
            "card_id": card_info.card_id,
            "card_name": card_info.card_name,
            "card_mp": card_info.card_id,
            "vip_code": card_info.vip_code,
            "expiration": card_info.expiration,
            "cert_type": cert_info.cert_type,
            "cert_id": cert_info.cert_id,
            "cert_validity_type": cert_info.cert_validity_type,
            "cert_begin_date": cert_info.cert_begin_date,
            "cert_end_date": cert_info.cert_end_date,

        }

        if not kwargs.get("order_id"):
            required_params["order_id"] = generate_mer_order_id()
        if not kwargs.get("order_date"):
            required_params["order_date"] = generate_req_date()
        if not kwargs.get("product_id"):
            required_params["product_id"] = OppsClient.mer_config.product_id

        required_params.update(kwargs)

        return request_post("/ssproxy/verifyCardApply", required_params)

    @classmethod
    def bind_confirm(cls, huifu_id, trans_amt, goods_desc, auth_code, notify_url, **kwargs):
        """
        快捷/代扣绑卡确认接口
        :param huifu_id: 商户号
        :param trans_amt: 交易金额
        :param goods_desc: 商品描述
        :param auth_code: 支付码
        :param notify_url: 异步回调地址（virgo://http://www.xxx.com/getResp）
        :param kwargs: 额外参数
        :return: 支付结果
        """
        required_params = {
            "huifu_id": huifu_id,
            "auth_code": auth_code,
            "trans_amt": trans_amt,
            "goods_desc": goods_desc,
            "notify_url": notify_url
        }

        if not kwargs.get("mer_ord_id"):
            kwargs["mer_ord_id"] = generate_mer_order_id()

        # TODO 确认风控信息
        if not kwargs.get("risk_check_info"):
            kwargs["risk_check_info"] = ""

        required_params.update(kwargs)
        return request_post("/ssproxy/verifyCardConfirm", required_params)

    @classmethod
    def un_bind(cls, huifu_id, org_req_date, **kwargs):
        """
        快捷/代扣解绑接口
        :param huifu_id: 商户号
        :param org_req_date: 原始订单请求时间
        :param kwargs: 额外参数
        :return: 支付对象
        """

        required_params = {
            "huifu_id": huifu_id,
            "req_date": org_req_date,
        }
        # sys_id 不传默认用SDK 初始化时配置信息，没有配置，使用商户号
        if not kwargs.get("sys_id"):
            mer_config = OppsClient.mer_config
            sys_id = mer_config.sys_id
            if len(mer_config.sys_id) == 0:
                sys_id = huifu_id

            required_params["sys_id"] = sys_id

        required_params.update(kwargs)
        return request_post_without_seq_id("/ssproxy/unBind", required_params)

    @classmethod
    def pay(cls, huifu_id, ord_amt, notify_url, **kwargs):
        """
        快捷支付申请接口
        :param huifu_id: 商户号
        :param ord_amt: 退款金额
        :param notify_url: 异步回调地址
        :param kwargs: 额外参数
        :return:  退款对象
        """
        required_params = {
            "huifu_id": huifu_id,
            "ord_amt": ord_amt,
            "notify_url": notify_url
        }

        if not kwargs.get("mer_ord_id"):
            kwargs["mer_ord_id"] = generate_mer_order_id()

        # TODO 确认风控信息
        if not kwargs.get("risk_check_info"):
            kwargs["risk_check_info"] = ""

        required_params.update(kwargs)

        return request_post("/top-online-ser/quickpay/apply", required_params)

    @classmethod
    def pay_confirm(cls, huifu_id, org_req_date, **kwargs):
        """
        快捷支付确认接口
        :param huifu_id: 商户号
        :param org_req_date: 原始退款请求时间
        :param kwargs: 额外参数
        :return:
        """
        required_params = {
            "huifu_id": huifu_id,
            "req_date": org_req_date,
        }
        # sys_id 不传默认用SDK 初始化时配置信息，没有配置，使用商户号
        if not kwargs.get("sys_id"):
            mer_config = OppsClient.mer_config
            sys_id = mer_config.sys_id
            if len(mer_config.sys_id) == 0:
                sys_id = huifu_id

            required_params["sys_id"] = sys_id

        required_params.update(kwargs)
        return request_post_without_seq_id("/top-online-ser/quickpay/confirm", required_params)
