import json
import logging
import asyncio
import aiohttp


async def send(url, data={}, fmt='json', timeout=5, retry=1):
    ret = None
    while retry > 0:
        retry -= 1
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, data=data, timeout=timeout) as res:
                    if res.status in [200, 201, 204]:
                        if fmt == 'text':
                            ret = await res.text()
                        elif fmt == 'json':
                            ret = await res.text(encoding='utf-8', errors='replace')
                            ret = json.loads(ret)
                        else:
                            ret = await res.read()

                        break
                    else:
                        # ret = await res.read()
                        logging.debug('aioHttpDelete fail! url:%s, status:%d, retry:%d' % (
                        url, res.status, retry))
        except Exception as ex:
            if type(ex) == asyncio.TimeoutError:
                logging.warn('aioHttpDelete timeout, url:%s' % url)
            else:
                logging.warn('exception when aioHttpDelete, url:%s, err:%s, type:%s' % (
                url, str(ex), type(ex)))
                break

    if not ret:
        logging.warn('aioHttpDelete fail! url:%s' % (url))

    return ret
