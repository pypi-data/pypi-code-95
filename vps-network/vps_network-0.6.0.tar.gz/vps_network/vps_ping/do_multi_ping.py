import logging
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import List, Optional

from icmplib import (
    PID,
    resolve,
    is_ipv6_address,
    ICMPv4Socket,
    ICMPv6Socket,
    ICMPRequest,
    ICMPLibError,
)
from rich.progress import Progress, BarColumn, TimeRemainingColumn

from .data_type import PingResult

__all__ = ["do_multi_ping", "do_one_ping"]


def do_one_ping(
    host,
    progress: Progress,
    cc: Optional[str] = None,
    seq_offset=0,
    count=8,
    interval=0.1,
    timeout=2,
    id=PID,
    source=None,
    **kwargs,
) -> PingResult:
    """
    :raises NameLookupError: If you pass a hostname or FQDN in
        parameters and it does not exist or cannot be resolved.
    :raises SocketPermissionError: If the privileges are insufficient
        to create the socket.
    :raises SocketAddressError: If the source address cannot be
        assigned to the socket.
    :raises ICMPSocketError: If another error occurs. See the
        `ICMPv4Socket` or `ICMPv6Socket` class for details.
    """

    address = resolve(host)
    if isinstance(address, list):
        address = address[0]

    log = logging.getLogger("rich")

    task_id = progress.add_task(host, total=count)

    # on linux `privileged` must be True
    if is_ipv6_address(address):
        sock = ICMPv6Socket(address=source, privileged=True)
    else:
        sock = ICMPv4Socket(address=source, privileged=True)

    times = []

    for sequence in range(count):
        progress.update(task_id, advance=1)

        request = ICMPRequest(
            destination=address, id=id, sequence=sequence + seq_offset, **kwargs
        )

        try:
            sock.send(request)

            reply = sock.receive(request, timeout)
            reply.raise_for_status()

            round_trip_time = (reply.time - request.time) * 1000
            times.append(round_trip_time)

            if sequence < count - 1:
                sleep(interval)

        except ICMPLibError as e:
            log.error(f"接收 {host} Ping 返回信息失败: {e}")

    progress.remove_task(task_id=task_id)

    sock.close()

    log.info(f"{host} Ping 检测已经完成")

    return PingResult(host=host, cc=cc, count=count, times=times)


def do_one_ping_wrapper(**kwargs) -> Optional[PingResult]:
    try:
        return do_one_ping(**kwargs)
    except Exception as e:
        log = logging.getLogger("rich")
        log.error(f"ping {kwargs.get('host')} failed: {e}")
        return None


def do_multi_ping(
    hosts: dict, count: int = 8, interval: float = 0.01, timeout: int = 2
) -> List[PingResult]:
    pool = ThreadPoolExecutor(thread_name_prefix="ping")

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "{task.completed} / {task.total}",
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        jobs = []
        offset = 0
        for host, cc in hosts.items():
            offset += 1
            job = pool.submit(
                do_one_ping_wrapper,
                seq_offset=offset * len(hosts) * count,
                host=host,
                cc=cc,
                count=count,
                interval=interval,
                timeout=timeout,
                progress=progress,
            )
            jobs.append(job)
            sleep(0.5)  # fixme there is a deadlock in rich, need more inspect

        results: List[Optional[PingResult]] = list(map(lambda x: x.result(), jobs))
        results: List[PingResult] = list(filter(lambda x: x is not None, results))

    return results
