import httpx
from scan.response import Response
from scan.common import logger


class Downloader(object):
    def __init__(self):
        self.client = None
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko)'
        }

    async def close(self):
        try:
            await self.client.aclose()
        except:
            pass

    @staticmethod
    async def log_request(request):
        pass

    @staticmethod
    async def log_response(response):
        """
        日志钩子
        """
        request = response.request
        await logger.info(f'{response.status_code}  {request.url}')

    async def request(self, url, params=None, headers=None, cookies=None, auth=None, proxies=None, allow_redirects=True,
                      content=None, data=None, files=None, json=None, timeout=30, cycle=3):
        if data or json or content:
            method = 'POST'
        else:
            method = 'GET'
        for _ in range(cycle):
            try:
                if not proxies:
                    if not self.client:
                        self.client = httpx.AsyncClient(event_hooks={'response': [self.log_response]})
                    resp = await self.client.request(
                        method=method, url=url, content=content, data=data, files=files, json=json, params=params,
                        headers=headers, cookies=cookies, auth=auth, allow_redirects=allow_redirects, timeout=timeout
                    )
                    response = Response(resp)
                    return response
                else:
                    async with httpx.AsyncClient(proxies=proxies, event_hooks={'response': [self.log_response]}) as client:
                        resp = await client.request(
                            method=method, url=url, content=content, data=data, files=files, json=json, params=params,
                            headers=headers, cookies=cookies, auth=auth, allow_redirects=allow_redirects,
                            timeout=timeout
                        )
                        response = Response(resp)
                        return response
            except Exception as e:
                await logger.error(f'Failed to request {url}  {e}')




