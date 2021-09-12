import functools
import time

from requests.exceptions import ConnectionError

from robot.api import logger

def retry_on_exception(func):
    
    @functools.wraps(func)
    def retry_helper(self, *args, **kwargs):
        current_retry = 0
        current_delay = kwargs.get('delay', self._delay)
        backoff_factor = kwargs.get('backoff_factor', self._backoff_factor)
        max_retries = kwargs.get('max_retries', self._max_retries)

        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
    
        signature = ", ".join(args_repr + kwargs_repr)
    
        logger.debug(f"Calling retry for {func.__name__}({signature})")

        logger.debug(f"_max_retries: {max_retries}")
        logger.debug(f"_backoff_factor: {backoff_factor}")
        logger.debug(f"_delay: {current_delay}")
        
        while True:
            try:
                value = func(self, *args, **kwargs)
    
                logger.debug(f"{func.__name__!r} returned {value!r}")
            
                return value
                
            except ConnectionError as e:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * backoff_factor
                
                if current_retry > max_retries:
                    raise Exception(f"Calling {func.__name__} with max_retries {max_retries} without success.") from e

                logger.info(f"[{func.__name__}] Retry count: {current_retry}; delay: {current_delay}")

    return retry_helper
