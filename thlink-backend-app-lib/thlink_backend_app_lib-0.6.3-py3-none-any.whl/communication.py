try:
    import requests
    import urllib3.util.retry

    http = requests.Session()

    retry = urllib3.util.retry.Retry(
        total=3,
        backoff_factor=0.2,
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=True,
        redirect=3,
        raise_on_redirect=True,
    )
    retry.BACKOFF_MAX = 2

    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    http.mount("https://", adapter)
    http.mount("http://", adapter)

except ImportError:
    pass
