from functools import wraps
from regia.container import Mapping


# 注册路由
def route(rule: str, **options):
    def wrapper(view_func):
        endpoint = options.pop("endpoint", None)
        mapping = Mapping()
        item = {'rule': rule, 'endpoint': endpoint, 'view_func': view_func, 'options': options}
        mapping.register(item)

        @wraps(view_func)
        def inner(*args, **kwargs):
            return view_func(*args, **kwargs)

        return inner

    return wrapper
