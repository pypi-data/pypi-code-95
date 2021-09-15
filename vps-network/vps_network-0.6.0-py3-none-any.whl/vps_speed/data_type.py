from typing import Optional

from pydantic import BaseModel, Field

__all__ = ["SpeedServer", "SpeedClient", "SpeedResult"]


class SpeedServer(BaseModel):
    url: str = Field(..., title="网页地址")
    lat: str = Field(..., title="经度")
    lon: str = Field(..., title="纬度")
    name: str = Field(..., title="名称")
    country: str = Field(..., title="国家")
    cc: str = Field(..., title="国家代码", description="国家代码的缩写")
    sponsor: str = Field(..., title="贡献者")
    id: str = Field(..., title="服务器ID")
    host: str = Field(..., title="服务器地址")
    d: float = Field(..., title="")
    latency: float = Field(..., title="延迟")


class SpeedClient(BaseModel):
    ip: str = Field(..., title="")
    lat: str = Field(..., title="经度")
    lon: str = Field(..., title="纬度")
    isp: str = Field(..., title="ISP 提供商")
    isprating: str = Field(..., title="")
    rating: str = Field(..., title="")
    ispdlavg: str = Field(..., title="")
    ispulavg: str = Field(..., title="")
    loggedin: str = Field(..., title="")
    country: str = Field(..., title="")


class SpeedResult(BaseModel):
    download: float = Field(..., title="下载速度", description="注意单位是: bit 不是字节")
    upload: float = Field(..., title="上传速度", description="注意单位是: bit 不是字节")
    ping: float = Field(..., title="ping")
    server: SpeedServer = Field(..., title="服务器")
    timestamp: str = Field(..., title="时间", description="RFC3389 时间字符串")
    bytes_sent: Optional[int] = Field(None, title="发送字节")
    bytes_received: Optional[int] = Field(None, title="接受字节")
    client: SpeedClient = Field(..., title="客户端信息")
