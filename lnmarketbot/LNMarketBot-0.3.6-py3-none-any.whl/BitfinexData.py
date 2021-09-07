import asyncio
import time
import pandas as pd
from .Data import Data

from bfxapi import Client


class BitfinexData(Data):

    def __init__(self, symbol='tBTCUSD', timeframe='1m', start=0, **params):
        self.bfx = Client(
            logLevel='DEBUG',
        )
        switcher = {
            '1m': 1*60,
            '5m': 5*60,
            '15m': 15*60,
            '30m': 30*60,
            '1h': 1*60*60,
            '3h': 3*60*60,
            '6h': 6*60*60,
            '12h': 12*60*60,
            '1D': 1*24*60*60,
            '7D': 7*24*60*60,
            '14D': 14*24*60*60,
            '1M': 1*30*24*60*60,
            }
        self.timeframe = timeframe
        self.interval = switcher.get(timeframe, 60)
        self.start = start
        self.symbol = symbol
        self.ohlc = pd.DataFrame(columns=[
            'open',
            'high',
            'low',
            'close',
            'volume',
        ], index=pd.to_datetime([]))
        super().__init__(**params)

    async def dataGenerator(self):
        now = int(round(time.time() * 1000))
        wait = 60
        maxRows = 2880
        blockSize = 1440
        retry = 0
        timer = None
        while retry < 10:
            if timer is not None:
                await timer

            try:
                candles = await self.bfx.rest.get_public_candles(
                    symbol=self.symbol,
                    start=self.start,
                    end=now,
                    tf=self.timeframe,
                )
            except Exception:
                await asyncio.sleep(wait)
                retry += 1
                continue

            retry = 0
            for c in candles:
                self.ohlc.loc[pd.to_datetime(c[0], unit='ms').floor('s')] = [
                    c[1],
                    c[3],
                    c[4],
                    c[2],
                    c[5],
                ]
            self.ohlc.sort_index(inplace=True)
            self.start = now
            if len(self.ohlc) >= maxRows:
                self.ohlc.drop(self.ohlc.head(blockSize).index,
                               inplace=True)
            timer = asyncio.create_task(asyncio.sleep(self.interval))
            yield self.ohlc
        raise ConnectionError("Retry Exceeded 10")

    def test(self):
        async def BitfinexDataTest(bfx, symbol, start, timeframe):
            ohlc = pd.DataFrame(columns=[
                'open',
                'high',
                'low',
                'close',
                'volume',
            ], index=pd.to_datetime([]))
            now = int(round(time.time() * 1000))
            candles = await bfx.rest.get_public_candles(
                symbol=symbol,
                start=start,
                end=now,
                tf=timeframe,
            )
            for c in candles:
                ohlc.loc[pd.to_datetime(c[0], unit='ms').floor('s')] = [
                    c[1],
                    c[3],
                    c[4],
                    c[2],
                    c[5],
                ]
            ohlc.sort_index(inplace=True)
            return ohlc

        t = asyncio.ensure_future(BitfinexDataTest(
            self.bfx,
            self.symbol,
            self.start,
            self.timeframe)
        )
        return asyncio.get_event_loop().run_until_complete(t)
