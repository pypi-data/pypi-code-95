#执行时长装饰器
import datetime
def duration(fn):
    def wrapper(*args,**kwargs):
        start = datetime.datetime.now()
        inc = fn(*args,**kwargs)
        delta = (datetime.datetime.now()-start).total_seconds()
        print('{} took {:.2f}s'.format(fn.__name__,delta))
        return inc
    return wrapper


