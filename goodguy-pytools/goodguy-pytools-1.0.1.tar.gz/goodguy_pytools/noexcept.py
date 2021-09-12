import logging


def noexcept(ret=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                ans = func(*args, **kwargs)
                return ans
            except Exception as e:
                logger = logging.getLogger('goodguy')
                logger.exception(e)
            return ret

        return wrapper

    return decorator
