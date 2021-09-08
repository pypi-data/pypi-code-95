
import asyncio

import tornado.ioloop

import sanepg
from .connection import _Connection


# factory function to connect a pool
def connect(dsn, *args, **kwds):
    pool = Pool(dsn, *args, **kwds)
    ioloop = tornado.ioloop.IOLoop.current()
    try:
        return ioloop.run_sync(pool.connect)
    except sanepg.SaneError as e:
        raise


class Pool:
    def __init__(self, dsn, size=2, maxSize=None, **connectionKeywords):
        self._dsn    = dsn
        self.size    = size
        self.maxSize = maxSize

        self.connectionKeywords = connectionKeywords

        self._totalConnections = 0
        self._ioloop = tornado.ioloop.IOLoop.current()
        self._pool   = []

    def _addConnections(self, count):
        connectionFuture = asyncio.Future()
        connectionFuture.remaining = count

        def onConnect(f):
            connectionFuture.remaining -= 1
            if f.exception():
                connectionFuture.set_exception(sanepg.SaneError('%s', f.exception()))
                return

            self._totalConnections += 1
            self._pool.append(f.result())

            if connectionFuture.remaining == 0:
                connectionFuture.set_result(self)

        for idx in range(count):
            connection = _Connection(self._dsn, **self.connectionKeywords)
            self._ioloop.add_future(connection.connect(), onConnect)

        return connectionFuture

    def _getConnection(self):
        connectionFuture = asyncio.Future()
        try:
            connection = self._pool.pop()
            connectionFuture.set_result(connection)
        except IndexError:
            def onConnection(f):
                try:
                    connection = self._pool.pop()
                    connectionFuture.set_result(connection)
                except IndexError:
                    connectionFuture.set_exception(IOError('Unable to add connection'))
            self._ioloop.add_future(self._addConnections(1), onConnection)
        return connectionFuture

    def connect(self):
        return self._addConnections(self.size)

    def execute(self, statement, *args):
        execFuture = asyncio.Future()

        def onConnection(f):
            connection = f.result()
            def onFinish(f):
                self._pool.append(connection)

            connection.execute(execFuture, statement, *args)
            self._ioloop.add_future(execFuture, onFinish)

        self._ioloop.add_future(self._getConnection(), onConnection)
        return execFuture

    def execute_values(self, statement, values):
        execFuture = asyncio.Future()

        def onConnection(f):
            connection = f.result()
            def onFinish(f):
                self._pool.append(connection)

            connection.execute_values(execFuture, statement, values)
            self._ioloop.add_future(execFuture, onFinish)

        self._ioloop.add_future(self._getConnection(), onConnection)
        return execFuture

