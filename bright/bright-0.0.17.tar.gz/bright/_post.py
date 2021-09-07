import json
import logging
import asyncio
import aiohttp


# fmt: text/json/bin
async def send(url, data={}, fmt='json', timeout=5, retry=1, headers={}):
    ret = None
    while retry > 0:
        retry -= 1
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, timeout=timeout, headers=headers) as res:
                    if fmt == 'text':
                        ret = await res.text()
                    elif fmt == 'json':
                        ret = await res.text(encoding='utf-8')
                        ret = json.loads(ret)
                    else:
                        ret = await res.read()
        except Exception as ex:
            if type(ex) == asyncio.TimeoutError:
                logging.warn('aioHttpPost timeout, url:%s' % url)
            else:
                logging.warn('exception when aioHttpPost, url:%s, err:%s, type:%s' % (
                url, str(ex), type(ex)))
                break

    if not ret:
        logging.warn('aioHttpPost fail! url:%s' % (url))

    return ret
