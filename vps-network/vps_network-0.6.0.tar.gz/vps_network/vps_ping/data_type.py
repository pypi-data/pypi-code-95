from typing import List

from pydantic import BaseModel, Field

__all__ = ["PingResult"]


class PingResult(BaseModel):
    host: str = Field(..., title="目的服务器", description="从本机Ping的目的服务器")
    cc: str = Field(None, title="国家编码", description="目标服务器所在的国家编码")
    count: int = Field(..., title="请求次数", description="一共发送了多少次请求")
    times: List[float] = Field(
        ...,
        title="RTT时间",
        description="rtt(round trip time)列表, 注意: 时间单位为 ms, len(times) 数量可能少于 count 表示有部分数据丢失",
    )

    def __str__(self) -> str:
        return f"<PingResult Host: {self.host} Times: {self.times}>"
