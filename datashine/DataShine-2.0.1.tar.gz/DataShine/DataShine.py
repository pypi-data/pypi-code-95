import asyncio
import functools
from copy import deepcopy


def _no_closed(method):
    '''
    Can not be run when closed.

    :return:
    '''

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        self = args[0]
        if self._closed:
            raise RuntimeError(f'{repr(self)} is already closed.')
        return method(*args, **kwargs)

    return wrapper


class DataShine:
    def __init__(self):
        self._unlocked = asyncio.Event()
        self._unlocked.set()
        self._period_change_event = asyncio.Event()
        self._data_container = None
        self._q = asyncio.Queue()  # todo 取消上层的Queue
        self._closed = False

    async def close(self):
        '''
        Close the DataShine instance.

        :return:
        '''
        self._closed = True

    @_no_closed
    async def push_data(self, data):
        '''
        Set the lamp to carry a data to be taken, and shine the data to notify monitors new data coming.

        :param data:
        :return:
        '''
        self._q.put_nowait(data)

    @property
    def data(self):
        '''
        Query the data last pushed.

        :return:
        '''
        return self._data_container

    @_no_closed
    async def wait_data_shine(self):
        '''
        Wait the shined data. If you wait too later, you will lose the chance to get the data. If you can not wait the data
        in time every time but have to handle all the data, you can cache data in a instance of asyncio.Queue.
        fixme 还是多层分发Queue吧

        :return:
        '''
        await asyncio.create_task(self._period_change_event.wait())
        return deepcopy(self._data_container)


# todo 多层分发Queue可以用原生的Queue实现，这个库没什么用，准备删除。AsyncGear不能作为传递数据的方式，有问题

if __name__ == '__main__':
    async def test():
        pass


    asyncio.create_task(test())
