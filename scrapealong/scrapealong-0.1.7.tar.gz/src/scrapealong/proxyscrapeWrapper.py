# -*- coding: utf-8 -*-

from .common import logger

from diskcache import Cache
import tempfile
from tqdm import tqdm

import proxyscrape

collector = proxyscrape.create_collector('my-resource', 'http')

def loopOproxies(limit=100, bypass=False):
    if bypass is False:
        for ii in range(limit):
            res = collector.get_proxy({'code': ('it', 'de', 'nl', 'fr', 'ch',), 'anonymous': True})
            if res.type=='https':
                continue
            logger.debug(f"Using proxy: {res}")
            yield f"{res.type}://{res.host}:{res.port}"
    while True:
        yield None

@timeit
async def fetchWithProxyscrape(url, retry=3):
    """ WARNING! DO NOT USE IT!
    Fetches the given url and return the parsed page body
    DOC:
        * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    """
    timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        allProxies = loopOproxies(bypass=False)
        # proxy = next(allProxies)
        for proxy in allProxies:
            try:
                async with session.get(url, proxy=proxy) as response:
                    body = await response.text()
            except (
                aiohttp.client_exceptions.ClientHttpProxyError,
                aiohttp.client_exceptions.ClientOSError,
                aiohttp.client_exceptions.ClientProxyConnectionError,
            ) as err:
                logger.debug(f"ClientProxyError: {err}")
                proxy = next(allProxies)
                continue
            except (aiohttp.ClientConnectorError, asyncio.exceptions.TimeoutError,) as err:
                if proxy is None:
                    if retry>0:
                        await asyncio.sleep(RETRY_WITHIN)
                        retry -= 1
                        continue
                    else:
                        raise err
                else:
                    proxy = next(allProxies)
                    continue
            except Exception as err:
                logger.debug(err)
                import pdb; pdb.set_trace()
            else:
                if response.status>=400:
                    if retry>0:
                        retry -= 1
                        await asyncio.sleep(RETRY_WITHIN)
                        continue
                    raise Exception(response.status)
                break

            if proxy is None:
                rety -= 1

    return parser(body)
