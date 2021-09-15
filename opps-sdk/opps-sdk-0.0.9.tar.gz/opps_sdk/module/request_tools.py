# url path 统一管理 花括号中变量代表待替换值
from opps_sdk.core.api_request import ApiRequest
from opps_sdk.opps_client import OppsClient
from opps_sdk.common_util import generate_mer_order_id
import datetime

# ---------- 扫码支付 payment 对象----------
offline_payment_create = '/top/trans/pullPayInfo'  # 聚合正扫
offline_payment_scan = '/top/trans/authCodePay'  # 聚合反扫
offline_payment_close = '/toprrc/close'  # 交易关单
offline_payment_query = '/topqur/transQuery'  # 交易查询
offline_payment_refund = '/toprrc/refund'  # 交易查询
offline_payment_refund_query = '/topqur/refundQuery'  # 退款查询

union_user_id = '/top/trans/getUserMark'  # 获取银联用户标识


online_bind = '/top/trans/pullPayInfo'  # 聚合正扫






# 调用域名
#
BASE_URL = 'https://spin.cloudpnr.com'


def __request_init(url, request_params, base_url=BASE_URL):
    mer_config = OppsClient.mer_config
    if BASE_URL in url:
        ApiRequest.base_url = url
        url = ""
    else:
        ApiRequest.base_url  = BASE_URL

    # 公共参数，渠道商/代理商/商户的huifu_id （1）当主体为渠道商/代理商时，此字段填写渠道商/代理商huifu_id；
    # （2）当主体为直连商户时，此字段填写商户huifu_id

    huifu_id = mer_config.sys_id
    if len(mer_config.sys_id) == 0:
        huifu_id = request_params["huifu_id"]
    ApiRequest.build(mer_config.product_id, mer_config.private_key, mer_config.public_key, url,
                     request_params, huifu_id, OppsClient.connect_timeout)


def request_post(url, request_params, files=None, base_url=''):
    if not request_params.get('req_seq_id'):
        request_params['req_seq_id'] = generate_mer_order_id()

    if not request_params.get('req_date'):
        request_params['req_date'] = datetime.datetime.now().strftime('%Y%m%d')

    __request_init(url, request_params, base_url)
    return ApiRequest.post(files)


def request_post_without_seq_id(url, request_params, files=None, base_url=''):
    __request_init(url, request_params, base_url)
    return ApiRequest.post(files)


def request_get(url, request_params, base_url=''):
    __request_init(url, request_params, base_url)
    return ApiRequest.get()
