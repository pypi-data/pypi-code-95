from opps_sdk.module.request_tools import request_post, offline_payment_create, offline_payment_close, \
    offline_payment_query, offline_payment_refund, offline_payment_refund_query, offline_payment_scan, \
    request_post_without_seq_id
from opps_sdk.common_util import generate_mer_order_id
from opps_sdk.opps_client import OppsClient


class ScanPayment(object):
    """
    聚合正扫，聚合反扫，交易查询等
    """

    @classmethod
    def create(cls, huifu_id, trade_type, trans_amt, goods_desc, notify_url, *, open_id="", app_id="", buyer_id="",
               user_id="", client_ip="", **kwargs):
        """
        创建聚合正扫订单
        :param huifu_id:  商户号
        :param trade_type: 支付方式 微信公众号：T_JSAPI；小程序：T_MINIAPP； 支付宝JS：A_JSAPI；支付宝正扫：A_NATIVE；
        银联正扫： U_NATIVE；银联JS：U_JSAPI；数字人民币二维码支付：D_NATIVE；
        :param trans_amt: 支付金额
        :param goods_desc: 商品描述
        :param notify_url: 异步回调地址
        :param open_id: 微信 open_id
        :param app_id: 微信 app_id（小程序或者公众号）
        :param buyer_id: 支付宝买家ID
        :param user_id: 银联用户标识
        :param client_ip: 付款时的IP地址，银联JS支付必填
        :param kwargs:  额外参数
        :return: 支付对象
        """
        required_params = {
            "huifu_id": huifu_id,
            "trade_type": trade_type,
            "trans_amt": trans_amt,
            "goods_desc": goods_desc,
            "notify_url": notify_url
        }

        # 微信公众号：T_JSAPI；小程序：T_MINIAPP
        if trade_type == "T_JSAPI" or trade_type == "T_MINIAPP":
            if not kwargs.get("wx_data"):
                kwargs["wx_data"] = {
                    "sub_appid": app_id,
                    "sub_openid": open_id
                }

        # 支付宝JS
        if trade_type == "A_JSAPI":
            if not kwargs.get("alipay_data"):
                kwargs["alipay_data"] = {
                    "buyer_id": buyer_id
                }

        # 银联正扫：U_NATIVE；银联JS：U_JSAPI
        if trade_type == "U_NATIVE" or trade_type == "U_JSAPI":
            if not kwargs.get("unionpay_data"):
                kwargs["unionpay_data"] = {
                    "user_id": user_id,
                    "client_ip": client_ip
                }

        if not kwargs.get("mer_ord_id"):
            kwargs["mer_ord_id"] = generate_mer_order_id()
        kwargs["user_id"] = user_id
        required_params.update(kwargs)

        return request_post(offline_payment_create, required_params)

    @classmethod
    def scan_pay(cls, huifu_id, trans_amt, goods_desc, auth_code, notify_url, **kwargs):
        """
        聚合反扫
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
        return request_post(offline_payment_scan, required_params)

    @classmethod
    def query(cls, huifu_id, org_req_date, **kwargs):
        """
        支付查询
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
        return request_post_without_seq_id(offline_payment_query, required_params)

    @classmethod
    def refund(cls, huifu_id, ord_amt, notify_url, **kwargs):
        """
        退款
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

        return request_post(offline_payment_refund, required_params)

    @classmethod
    def query_refund(cls, huifu_id, org_req_date, **kwargs):
        """
        退款查询
        :param huifu_id: 商户号
        :param org_req_date: 原始退款请求时间
        :param kwargs: 额外参数
        :return: 退款对象
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
        return request_post_without_seq_id(offline_payment_refund_query, required_params)

    @classmethod
    def close(cls, huifu_id, org_req_seq_id, org_req_date, **kwargs):
        """
        关单请求
        :param huifu_id: 商户号
        :param org_req_seq_id: 原始订单请求流水号
        :param org_req_date: 原始订单请求日期
        :param kwargs: 额外参数
        :return: 关单对象
        """
        required_params = {
            "huifu_id": huifu_id,
            "org_req_date": org_req_date,
            "org_req_seq_id": org_req_seq_id
        }

        required_params.update(kwargs)
        return request_post(offline_payment_close, required_params)
