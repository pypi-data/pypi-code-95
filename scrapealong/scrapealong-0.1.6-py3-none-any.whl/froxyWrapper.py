# -*- coding: utf-8 -*-

from .common import logger
from froxy import Froxy
from diskcache import Cache
import tempfile
from tqdm import tqdm

def get_proxy_list():
    """ Returns a custom filtered proxy sequence """
    EXPIRE = 3600
    CACHE_PATH = tempfile.gettempdir()
    with Cache(CACHE_PATH, disk_pickle_protocol=3) as cache:
        try:
            proxyInstance = cache.get('proxyInstance')
            assert proxyInstance
        except (ValueError, AssertionError,):
            proxyInstance = Froxy()
            cache.set('proxyInstance', proxyInstance, EXPIRE)

    # WARNING! aiohttp library just support httl proxies
    return list(filter(lambda pp: pp[2][1]=='N', proxyInstance.http()))

def loopOproxies(bypass=False):
    if not bypass:
        for proxyInfo in tqdm(get_proxy_list()):
            logger.debug(f"Using proxy: {proxyInfo}")
            yield  f"http://{proxyInfo[0]}:{proxyInfo[1]}"
    while True:
        yield None

@timeit
async def fetchWithFroxy(url, retry=3):
    """ WARNING! DO NOT USE IT!
    Fetches the given url and return the parsed page body
    DOC:
        * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    """
    timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        allProxies = loopOproxies(bypass=False)
        proxy = next(allProxies)
        while True:
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
