from typing import Optional, List

from pydantic import Field, BaseModel

__all__ = ["TraceHop", "TraceResult"]


class TraceHop(BaseModel):
    """
    注意: 在 Traceroute 有可能在跟踪的时候 IP 地址也会发生变化
    但是我们并不考虑这个问题，要不然有可能导致后面没有办法画图
    也可以使用 fast 模式来避免这个问题。
    """

    ip: str = Field(..., title="IP地址")
    distance: int = Field(..., title="距离", description="当距离有跳跃的时候，说明中间有的地址被忽略")
    count: int = Field(..., title="请求数量", description="发送了多少个请求")
    times: List[float] = Field(
        ..., title="RTT时间", description="count - len(times)表示丢失的数量"
    )
    info: Optional[dict] = Field(
        None, title="IP信息", description="IP 信息，有可能获取失败，或者不存在(IP 地址为内网)"
    )


class TraceResult(BaseModel):
    host: str = Field(..., title="Trace目标地址")
    results: List[TraceHop] = Field(..., title="Trace结果")
