class apiconfig:
    apikey = None
    #apiprotocol = 'https://'
    #baseurl = '{}www.einfomax.co.kr/infomaxy/v1'.format(apiprotocol)
    apiprotocol = 'http://'
    baseurl = '{}localhost:5000/infomaxy/v1'.format(apiprotocol)

    verify_ssl = True
    use_retries = True
    retry_backoff_max = 8
    retry_total = 5
    retry_connect = 5
    retry_read = 5
    retry_forcelist = [429] + list(range(500, 512))
    retry_backoff_factor = 0.5
