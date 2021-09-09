PROXY_CHECK_URLS = [
    'https://api.ipify.org',
    'http://ifconfig.me/ip',
    'http://icanhazip.com/',
]
REQUEST_TIMEOUT = 40
MAX_CONCURRENCY_WORKERS = len(PROXY_CHECK_URLS)
