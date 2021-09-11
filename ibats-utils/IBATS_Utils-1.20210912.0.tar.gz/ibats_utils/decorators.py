"""
@author  : MG
@Time    : 2021/5/14 11:11
@File    : decorators.py
@contact : mmmaaaggg@163.com
@desc    : 用于封装各种工具装饰器
"""
import contextlib
import functools
import logging
import threading
import time
from typing import Optional, List

logger = logging.getLogger(__name__)


def thread_save(func):
    """线程安全装饰器，用于该函数执行过程线程安全"""
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        with lock:
            func(*args, **kwargs)

    return wrapper


class TryThread(threading.Thread):

    def __init__(self, target, *args, **kwargs):
        threading.Thread.__init__(self, target=target, args=args, kwargs=kwargs, name="try_thread")
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.ret = None

    def run(self):
        self.ret = self.target(*self.args, **self.kwargs)


def try_n_times(times=3, sleep_time=3, logger_obj: logging.Logger = None, exception=Exception, exception_sleep_time=0,
                timeout=None):
    """
    尝试最多 times 次，异常捕获记录后继续尝试
    :param times:
    :param sleep_time:
    :param logger_obj: 如果异常需要 log 记录则传入参数
    :param exception: 可用于捕获指定异常，默认 Exception
    :param exception_sleep_time: 当出现异常情况下，sleep n 秒
    :param timeout: 超时时间
    :return:
    """
    last_invoked_time: List[Optional[float]] = [None]

    def wrap_func(func):

        @functools.wraps(func)
        def try_it(*arg, **kwargs):
            ret_data = None
            for n in range(1, times + 1):
                if sleep_time > 0 and last_invoked_time[0] is not None \
                        and (time.time() - last_invoked_time[0]) < sleep_time:
                    time.sleep(sleep_time - (time.time() - last_invoked_time[0]))

                try:
                    if timeout is None or timeout <= 0:
                        ret_data = func(*arg, **kwargs)
                    else:
                        thread = TryThread(target=func, *arg, **kwargs)
                        thread.start()
                        wait_time = 0
                        while wait_time < timeout:
                            if thread.is_alive():
                                time.sleep(0.2)
                                wait_time += 0.2
                            else:
                                ret_data = thread.ret
                                break
                        else:
                            if logger_obj is not None:
                                logger_obj.warning("执行任务超时限(%ds)", timeout)
                            thread.join()
                            if logger_obj is not None:
                                logger_obj.warning("终止任务完成")
                            continue

                except:
                    if logger_obj is not None:
                        logger_obj.exception("第 %d 次调用 %s(%s, %s) 出错", n, func.__name__, arg, kwargs)
                    if exception_sleep_time is not None and exception_sleep_time > 0:
                        time.sleep(exception_sleep_time)
                    continue
                finally:
                    last_invoked_time[0] = time.time()

                break

            return ret_data

        return try_it

    return wrap_func


def timer(func):
    """
    为当期程序进行计时
    :param func:
    :return:
    """

    @functools.wraps(func)
    def timer_func(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.time()
            estimate = time.strftime('%H:%M:%S', time.gmtime(end - start))
            logger.info('%s 运行时间：%s 相关参数 (%s, %s)', func.__name__, estimate, args, kwargs)

    return timer_func


def no_with_if_is_none(with_sth: Optional[contextlib.AbstractContextManager]):
    return contextlib.nullcontext(with_sth) if with_sth is None else with_sth


def _test_no_with_if_is_none():
    import threading
    lock = threading.Lock()
    with lock:
        print(f'ok lock={lock}')
    with no_with_if_is_none(lock):
        print(f'no_with_if_is_none lock={lock}')
    lock = None
    with no_with_if_is_none(lock):
        print(f'no_with_if_is_none lock={lock}')


if __name__ == "__main__":
    _test_no_with_if_is_none()
