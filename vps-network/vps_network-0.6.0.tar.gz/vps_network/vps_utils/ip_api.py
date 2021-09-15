import ipaddress
from functools import lru_cache
from typing import Optional

import requests
from pydantic import BaseModel, Field

FIELDS = "status,continent,country,countryCode,region,regionName,city,isp,query,lat,lon"

__all__ = ["get_ip_info", "IPInfo"]


class IPInfo(BaseModel):
    query: str = Field(..., title="IP地址", description="查询的IP地址")
    status: str = Field(..., title="状态")
    continent: Optional[str] = Field(None, title="大洋")
    country: Optional[str] = Field(None, title="国家")
    countryCode: Optional[str] = Field(None, title="国家代码")
    region: Optional[str] = Field(None, title="区域")
    regionName: Optional[str] = Field(None, title="区域名称")
    city: Optional[str] = Field(None, title="城市")
    isp: Optional[str] = Field(None, title="ISP")
    lat: Optional[float] = Field(None, title="经度")
    lon: Optional[float] = Field(None, title="纬度")

    def is_success(self) -> bool:
        return self.status == "success"


@lru_cache(maxsize=64 * 1024)  # add lru cache to prevent hit rate limit
def get_ip_info(ip: str) -> Optional[IPInfo]:
    try:
        ip_a: ipaddress.IPv4Address = ipaddress.ip_address(ip)
        if ip_a.is_private:  # private address is ignored (MUST BE NO ANSWER)
            return None
    except ValueError:
        pass

    try:
        url = f"http://ip-api.com/json/{ip}?fields={FIELDS}&lang=zh-CN"
        resp: requests.Response = requests.get(url, timeout=5)
        if not resp.ok:
            return None
        info = IPInfo(**resp.json())
        if not info.is_success():
            return None
        return info
    except requests.Timeout:
        return None
