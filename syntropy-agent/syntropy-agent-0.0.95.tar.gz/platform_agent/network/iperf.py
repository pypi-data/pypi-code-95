#!/usr/bin/env python3
import iperf3

import logging
import threading
import time

logger = logging.getLogger()


class IperfServer(threading.Thread):

    def __init__(self):
        super().__init__()
        self.server = iperf3.Server()
        self.stop_iperf = threading.Event()
        self.daemon = True
        threading.Thread.__init__(self)

    @staticmethod
    def test_speed(hosts: list):
        now = int(time.time())
        results = {}
        client = iperf3.Client()
        for host in hosts:
            client.server_hostname = host
            result = client.run()
            data = [
                {
                    "time": now,
                    "host": host,
                    "fields": {
                        "upload": int(result.sent_Mbps),
                        "download": int(result.received_Mbps),
                        "retransmits": int(result.retransmits),
                    },
                }
            ]
            results[host] = data
            client.defaults()
        return results

    def run(self):
        while not self.stop_iperf.is_set():
            self.server.run()

    def join(self, timeout=None):
        self.stop_iperf.set()
        super().join(timeout)
