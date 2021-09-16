import functools
import asyncio


def except_cancelled(method):
    """
    异步装饰器装饰异步方法
    :param method: 被装饰协程（异步方法）
    :return:
    """

    @functools.wraps(method)
    async def wrapper(*args, **kwargs):
        # print(f'装饰器装饰{__name__}方法')
        try:
            # 此处必须await 切换调用被装饰协程，否则不会运行该协程
            await method(*args, **kwargs)
        except asyncio.exceptions.CancelledError:
            pass

    return wrapper
