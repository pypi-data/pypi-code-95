# 时间模块
import time

def timing(f):
    """测试函数执行时间

    用法 @timing，修饰特定方法即可

    Args:
        f ([type]): 方法
    """
    def wrap(*args):
        import time
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{:.2f}s'.format(time2 - time1), end=' ')
        return ret
    return wrap

