import requests

from .config import MobioEnvironment, UrlConfig
from .merchant_config import MerchantConfig
from .mobio_media_sdk import MobioMediaSDK


@MobioMediaSDK.lru_cache.add()
def get_host_by_merchant_id(
        admin_host=None,
        merchant_id=None,
        request_timeout=None,
        media_api_version=None
):
    MerchantConfig().set_adm_host(admin_host)
    merchant_config = MerchantConfig().get_merchant_config(merchant_id)
    host_media = merchant_config.get("media_host")
    token_value = merchant_config.get("p_t")
    host_url = str(UrlConfig.GET_HOST_BY_MERCHANT).format(
        host=host_media,
        version=media_api_version
    )
    request_header = {
        "X-Merchant-ID": merchant_id,
        "Authorization": token_value
    }
    try:
        response = requests.get(
            host_url,
            headers=request_header,
            timeout=request_timeout,
        )
        response.raise_for_status()
        result = response.json()
    except Exception as ex:
        print("media_sdks::get_host_by_merchant_id()::error: %s" % ex)
        result = dict()
    data = result.get("data", {})
    return data.get("host", MobioEnvironment.PUBLIC_HOST) if data else MobioEnvironment.PUBLIC_HOST

