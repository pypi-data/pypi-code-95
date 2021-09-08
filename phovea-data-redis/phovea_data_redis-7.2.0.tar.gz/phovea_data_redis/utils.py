import logging

_log = logging.getLogger(__name__)


def wait_for_redis_ready(db, timeout=None):
  import time
  import redis

  _log.info('check if redis is ready')
  start_time = time.time()
  while timeout is None or time.time() - start_time < timeout:
    try:
      db.dbsize()
    except redis.exceptions.BusyLoadingError:
      _log.info('stall till redis is ready')
      time.sleep(0.5)
    else:
        break
