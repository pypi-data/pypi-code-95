#!/usr/bin/env python3

import time
import requests
from typing import Optional
from CloudflareAPI.exceptions import APIError

class Fetch:
    def __init__(self, url: str):
        self.base_url = url

    def __call__(self, endpoint: str) -> Optional[str]:
        url = self.base_url + endpoint
        print("\rFetching URL:", url, end="")
        response = requests.get(url, timeout=4)
        if not response.ok:
            print("Waiting for response...", end="")
            while not response.ok:
                response = requests.get(url, timeout=4)
                time.sleep(1)
        print(" [OK]")
        return response.text or None


def wait_result(func, *args, **kargs):
    while True:
        try:
            result = func(*args, **kargs)
            return result
        except APIError:
            print("\rWaiting for result...", end="")
            time.sleep(0.1)
            continue
