import json
import logging
import asyncio
import aiohttp


async def send(url, data={}, fmt='json', timeout=5, retry=1, headers={}):
    ret = None

    while retry > 0:
        retry -= 1
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=data, timeout=timeout, headers=headers) as res:
                    if res.status == 200:
                        if fmt == 'text':
                            ret = await res.text()
                        elif fmt == 'json':
                            ret = await res.text()
                            if isinstance(ret, bytes):
                                ret = ret.decode(errors='replace')

                            ret = json.loads(ret)
                        else:
                            ret = await res.read()

                        break
                    else:
                        logging.warn('aioHttpGet fail! url:%s, status:%d, retry:%d' % (
                        url, res.status, retry))
        except Exception as ex:
            if type(ex) == asyncio.TimeoutError:
                pass
            else:
                logging.warn('exception when aioHttpGet, url:%s, err:%s, type:%s' % (
                url, str(ex), type(ex)))

    return ret
