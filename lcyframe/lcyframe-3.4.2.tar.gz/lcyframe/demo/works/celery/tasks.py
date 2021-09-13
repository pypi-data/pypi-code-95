# -*- coding: utf-8 -*-
import random, time
from celery import shared_task
from lcyframe.libs.celery_route import BaseTask
from lcyframe.libs.celery_route import BaseEvent
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(ignore_result=False)  # 普通函数装饰为 celery task
def func(x):
    """
    seleep时间随机
    任务多线程并发执行，谁先执行完毕，谁先输出结果
    :param x:
    :return:
    """
    n = round(random.random(), 2)
    time.sleep(n)
    logger.info('Adding {0} + {1}'.format(x, "e"))
    return x, n


class DefaultEvent(BaseEvent):
    queue = "for_task_A"

    @staticmethod
    @shared_task(bind=True)
    def bind(self, x):
        """
        bind=True时，task对象self会作为第一个参数自动传入
        :param self:
        :param x:
        :return:
        """
        print(self.app)
        return x

    @staticmethod
    @shared_task(ignore_result=False, queue=queue)  # 普通函数装饰为 celery task
    def add(x):
        """
        seleep时间随机
        任务多线程并发执行，谁先执行完毕，谁先输出结果
        :use self.application.celery.DefaultEvent.add.delay(111)
        :param x:
        :return:

        """
        n = round(random.random(), 2)
        time.sleep(n)

        # 同步调用add2，等待结果返回。不建议使用。如有需要，建议使用任务链
        result = DefaultEvent().add2(x)

        # 待测试
        # s = DefaultEvent.add2.apply_async(x)

        # 异步调用add2,不等待
        AsyncResult = DefaultEvent.add2.delay(x)
        result = AsyncResult.result

        return x, n

    @shared_task(bind=True, ignore_result=False)
    def add2(self, x):      # 实例方法，第一个参数self，bind=False时，需要在调用时传入空字符串；bind=True时，调用时不需要传入，此次self为task自身
        n = round(random.random(), 2)
        time.sleep(n)
        return x, n

    @staticmethod
    @shared_task(queue="for_task_A")
    def taskA(x):
        return x, "for_task_A"

    @staticmethod
    @shared_task(queue="for_task_B")
    def taskB(x):
        return x, "for_task_B"

    @staticmethod
    @shared_task(
                bind=True,                            # True时，task对象self，会作为第一个参数自动传入，可以使用任务对象的属性。self.xxx。当传递一下参数时，必须绑定
                name="tasks.retry",                   # 名称，默认用函数名
                queue='for_task_A',                   # 指定队列,优先级高于配置文件中的CELERY_ROUTES
                countdown=10,                         # 延迟10s执行
                max_retries=3,                        # 重试次数
                default_retry_delay=3,                # 默认重试的间隔时间，优先级低于countdown属性
                # autoretry_for=(ReadTimeout,),       # 添加要自动重试的异常，如果所有异常都需要重试可以写Exception，默认不写所有异常都重试。，也可以通过try..execpt 手动调用重试函数
                soft_time_limit=5,                    # 任务最大执行时间
                ignore_result=False,                  # 结果需要保存
                base=BaseTask                         # 基类
                )
    def retry(self, target_origin_id, to_user, txt):
        try:
            if True:
                raise self.retry(args=[target_origin_id, to_user, txt],
                                 countdown=BaseTask.backoff(self.request.retries)
                                 )
        except BaseException as e:
            print("retry end")

