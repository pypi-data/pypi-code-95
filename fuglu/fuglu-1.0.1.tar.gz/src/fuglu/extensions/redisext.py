# -*- coding: utf-8 -*-
#   Copyright 2009-2021 Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
import logging
import threading
import time

try:
    import redis
    from redis import StrictRedis
    STATUS = "redis installed, version: {}".format(redis.__version__)
    ENABLED = True
    REDIS2 = redis.__version__.startswith('2')
    try:
        redisversion = [int(x) for x in redis.__version__.split('.')]
        REDIS33X = (redisversion[0] == 3 and redisversion[1] >= 3) or redisversion[0] > 3
    except Exception:
        REDIS33X = None
except ImportError:
    STATUS = "redis not installed"
    ENABLED = False
    StrictRedis = object
    redis = None
    REDIS33X = None


class RedisKeepAlive(StrictRedis):
    """
    Wrap standard Redis client to include a thread that
    will keep sending a ping to the server which will prevent
    connection timeout due to "timeout" setting in "redis.conf"

    Issue on github:
    https://github.com/andymccurdy/redis-py/issues/722
    """

    def __init__(self, *args, **kwargs):

        # check if pinginterval is given in kwargs
        self._pinginterval = kwargs.pop("pinginterval", 0)
        self._noisy = False
        self.pingthread = None

        if self._pinginterval:
            try:
                # since redis 3.3.x there should be a variable "healtch_check_interval" which is doing exactly
                # the pinginterval manually implemented before...
                super(RedisKeepAlive, self).__init__(*args, **kwargs, health_check_interval=self._pinginterval)
                logging.getLogger("fuglu.RedisKeepAlive").debug(f"Set ping interval {self._pinginterval} "
                                                                f"for redis {redis.__version__} using "
                                                                f"parameter health_check_interval")
            except Exception as e:
                if REDIS33X:
                    logging.getLogger("fuglu.RedisKeepAlive").error(f"Setting ping interval {self._pinginterval} "
                                                                    f"for redis {redis.__version__}: {str(e)}")
                super(RedisKeepAlive, self).__init__(*args, **kwargs)

                # start a thread which will ping the server to keep
                self.pingthread = threading.Thread(target=self.ping_and_wait)
                self.pingthread.daemon = True
                self.pingthread.start()
        else:
            # no ping interval, nothing special to do...
            super(RedisKeepAlive, self).__init__(*args, **kwargs)

    def ping_and_wait(self):
        """Send a ping to the Redis server to keep connection alive"""
        while True:
            if self._noisy:
                import logging
                logging.getLogger("fuglu.RedisKeepAlive").debug("Sending ping to Redis Server")
            self.ping()
            time.sleep(self._pinginterval)



class RedisPooledConn(object):
    def __init__(self, redis_url=None, **args):
        self.logger = logging.getLogger('fuglu.RedisPooledConn')
        if 'password' in list(args.keys()) and args['password']:
            self.logger.warning(f'deprecated redis password config - include it in redis_conn URL')
        elif 'password' in list(args.keys()) and not args['password']:
            del args['password']
        self._pinginterval = args.pop("pinginterval", 0)
        
        if not redis_url:
            self.pool = None
        elif '://' in redis_url:
            self.pool = redis.ConnectionPool(**args)
            self.pool = self.pool.from_url(redis_url)
        else:
            self.logger.warning(f'deprecated redis connection string {redis_url}')
            host, port, db = redis_url.split(':')
            self.pool = redis.ConnectionPool(host=host, port=port, db=int(db), **args)


    def get_conn(self):
        args = {}
        if self._pinginterval > 0:
            args['pinginterval'] = self._pinginterval
        return RedisKeepAlive(connection_pool=self.pool, **args)
    
    
    def check_connection(self):
        if self.pool is None:
            return False
        else:
            redisconn = self.get_conn()
            return redisconn.ping()



class ExpiringCounter(object):
    
    def __init__(self, redis_pool:RedisPooledConn=None, ttl=0, maxcount=0):
        self.redis_pool = redis_pool or RedisPooledConn()
        self.ttl = ttl
        self.maxcount = maxcount
    
    
    def _to_int(self, value, default:int=0):
        """
        Convert to integer if possible

        Args:
            value (str,unicode,bytes): string containing integer
        Keyword Args:
            default (int): value to be returned for conversion errors

        Returns:
            (int) value from string or default value

        """
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = default
        return value
    
    
    def increase(self, key:str, value:int=1):
        """
        Given the identifier, create a new entry for current time with given value.
        Args:
            key (str): identifier
            value (int): value to set (increase) for current key and timestamp

        Returns:
            (int): return the increased counter value

        """
        redisconn = self.redis_pool.get_conn()
        if self.maxcount > 0:
            try:  # only increase if value is not already very high
                values = redisconn.hgetall(key)
                if len(values) > self.maxcount:
                    return len(values)
            except redis.exceptions.TimeoutError:
                return 0

        try:
            ts = int(time.time()) + self.ttl
            pipe = redisconn.pipeline()
            # increase the the value of 'ts' by 'value' for hash 'key'
            pipe.hincrby(key, ts, value) # returns the value of redis[key][ts], usually same as param value
            pipe.expire(key, self.ttl)  # returns None, this is a safety measure to avoid stale keys
            result = pipe.execute()
            return result[0]
        except redis.exceptions.TimeoutError:
            return 0
    
    
    def get_count(self, key:str, cleanup:bool=True):
        """
        Get value. This is the sum of the count values within the ttl value stored in the class.
        Args:
            key (str): identifier
            cleanup (bool): Remove stale keys

        Returns:
            (int) aggregated value
        """
        count = 0
        delkeys = []
        redisconn = self.redis_pool.get_conn()
        values = redisconn.hgetall(key)
        ts = int(time.time())
        for k, v in values.items():
            if self._to_int(k) > ts:  # only count current keys
                count += self._to_int(v)
            elif cleanup:  # mark stale keys for cleanup
                delkeys.append(k)
        
        if delkeys and len(delkeys) == len(values):
            # all keys are stale
            redisconn.delete(key)
        elif delkeys:
            redisconn.hdel(key, *delkeys)
        
        return count
    
    
    def cleanup(self):
        """
        Remove stale entries from redis database
        """
        ts = int(time.time())
        redisconn = self.redis_pool.get_conn()
        for key in redisconn.scan_iter(match='*'):
            delete = False
            values = redisconn.hgetall(key)
            if not values:
                delete = True
            else:
                delkeys = []
                for k, v in values.items():
                    if self._to_int(k) <= ts:
                        delkeys.append(k)
                if delkeys and len(delkeys) == len(values):
                    delete = True
                elif delkeys:
                    redisconn.hdel(key, *delkeys)
            if delete:
                redisconn.delete(key)