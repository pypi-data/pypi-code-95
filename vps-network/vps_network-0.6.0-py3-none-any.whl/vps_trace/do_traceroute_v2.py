import logging
from time import sleep
from typing import List, Optional

from icmplib import (
    PID,
    resolve,
    is_ipv6_address,
    ICMPv4Socket,
    ICMPv6Socket,
    ICMPRequest,
    TimeExceeded,
    ICMPLibError,
    ICMPReply,
)

from .data_type import TraceHop, TraceResult
from ..vps_utils.ip_api import get_ip_info

__all__ = ["do_traceroute_v2", "do_traceroute_v2_wrapper"]


def do_traceroute_v2_wrapper(**kwargs) -> Optional[TraceResult]:
    try:
        return do_traceroute_v2(**kwargs)
    except Exception as e:
        log = logging.getLogger("rich")
        log.error(f"traceroute {kwargs.get('address')} 失败: {e}")
        return None


# noinspection PyIncorrectDocstring
def do_traceroute_v2(
    host: str,
    count: int = 2,
    interval: float = 0.05,
    timeout: int = 3,
    id: int = PID,
    first_hop: int = 1,
    max_hops: int = 32,
    source: Optional[str] = None,
    fast: bool = False,
    **kwargs,
) -> TraceResult:
    """
    :param table: rich 动态表格

    参数的含义与: `icmplib.traceroute` 保持一致
    """

    address = resolve(host)
    if isinstance(address, list):
        address = address[0]

    if is_ipv6_address(address):
        sock = ICMPv6Socket(source)
    else:
        sock = ICMPv4Socket(source)

    ttl = first_hop
    host_reached = False
    hops: List[TraceHop] = []

    while not host_reached and ttl <= max_hops:
        hop_address = None
        packets_sent = 0
        packets_received = 0

        times: List[float] = []

        for sequence in range(count):
            request = ICMPRequest(
                destination=address, id=id, sequence=sequence, ttl=ttl, **kwargs
            )

            reply: Optional[ICMPReply] = None
            try:
                sock.send(request)
                packets_sent += 1

                reply = sock.receive(request, timeout)
                reply.raise_for_status()
                host_reached = True

            except TimeExceeded:
                sleep(interval)

            except ICMPLibError:
                continue

            assert reply is not None

            hop_address = reply.source
            packets_received += 1

            round_trip_time = (reply.time - request.time) * 1000

            times.append(round_trip_time)

            if fast:
                break

        if packets_received:
            ip_info = get_ip_info(hop_address)

            info = ip_info.dict() if ip_info is not None else dict()

            hop = TraceHop(
                ip=hop_address, distance=ttl, count=count, times=times, info=info
            )

            hops.append(hop)

        ttl += 1

    sock.close()

    return TraceResult(results=hops, host=host)
