import os
import asyncio
from bfxapi import Client, Order
from .Broker import Broker
from .Notifier import addMessage


class BitfinexMBroker(Broker):

    def __init__(self):
        self.bfx = Client(
            API_KEY=os.getenv("BFX_KEY"),
            API_SECRET=os.getenv("BFX_SECRET"),
            logLevel='DEBUG',
        )

    @addMessage
    def order(self, symbol, price, quantity, leverage, stoploss=None):
        async def create_order(bfx, symbol, price, quantity, leverage,
                               stoploss=None):
            if stoploss is None:
                response = await bfx.rest.submit_order(
                    symbol=symbol,
                    amount=quantity,
                    leverage=leverage,
                    price=price,
                )
            else:
                response = await bfx.rest.submit_order(
                    symbol=symbol,
                    amount=quantity,
                    leverage=leverage,
                    price=price,
                    market_type=Order.Type.STOP_LIMIT,
                    oco_stop_price=stoploss,
                    oco=True,
                )
                # response is in the form of a Notification object
            return response

        t = asyncio.ensure_future(create_order(
            bfx=self.bfx,
            symbol=symbol,
            quantity=quantity,
            leverage=leverage,
            price=price,
            stoploss=stoploss
        ))
        response = asyncio.get_event_loop().run_until_complete(t)
        for o in response.notify_info:
            self.notifier.notify('Order: '+o)
