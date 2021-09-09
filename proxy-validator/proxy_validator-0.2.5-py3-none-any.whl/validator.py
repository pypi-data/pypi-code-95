import concurrent.futures
from typing import List

import requests

from proxy_validator.proxy_type import ProxyType
from proxy_validator.settings import PROXY_CHECK_URLS, MAX_CONCURRENCY_WORKERS, REQUEST_TIMEOUT


class ProxyValidator:
    @classmethod
    def is_valid_proxy(
        cls,
        username: str,
        password: str,
        ip: str,
        port: int,
        proxy_type: 'ProxyType',
        proxy_check_urls: List[str] = None
    ) -> bool:
        proxy_param = cls._get_request_param(
            username=username,
            password=password,
            ip=ip,
            port=port,
            proxy_type=proxy_type,
        )
        return cls._validate_proxy(ip, proxy_param, proxy_check_urls)

    @classmethod
    def _get_request_param(
        cls,
        username: str,
        password: str,
        ip: str,
        port: int,
        proxy_type: 'ProxyType'
    ) -> dict:
        protocol = ProxyType.protocols.get(proxy_type, '')
        url = '{proxy_type}://{proxy_credentials}/'.format(
            proxy_type=proxy_type,
            proxy_credentials=cls._collect_proxy_credentials(
                username=username,
                password=password,
                ip=ip,
                port=port,
            )
        )
        return {protocol: url}

    @classmethod
    def _collect_proxy_credentials(
        cls,
        username: str,
        password: str,
        ip: str,
        port: int,
    ) -> str:
        return '{username}:{password}@{ip}:{port}'.format(
            username=username,
            password=password,
            ip=ip,
            port=port,
        )

    @classmethod
    def _validate_proxy(cls, ip: str, proxy_param: dict, proxy_check_urls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY_WORKERS) as executor:
            future_to_url = {
                executor.submit(cls._check_proxy_in_url, ip, url, proxy_param): url for url in
                proxy_check_urls or PROXY_CHECK_URLS
            }
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    is_valid = future.result()
                    if is_valid:
                        executor.shutdown()
                        return is_valid
                except Exception:
                    pass
            return False

    @classmethod
    def _check_proxy_in_url(cls, ip: str, url: str, proxy_param: dict):
        response = requests.get(url, timeout=REQUEST_TIMEOUT, proxies=proxy_param)
        response.raise_for_status()
        return ip == response.content.decode()
