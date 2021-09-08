# -*- coding: UTF-8 -*-
# based on the ratelimit plugin in the postomaat project (https://gitlab.com/fumail/postomaat)
# developed by @ledgr

import time
from collections import defaultdict
from threading import Lock
from datetime import timedelta

from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, DeclarativeBase
from .backendint import BackendInterface
from fuglu.extensions.redisext import RedisPooledConn, ENABLED as REDIS_AVAILABLE

AIOREDIS_AVAILABLE = 0
try:
    import asyncio
    import aioredis
    AIOREDIS_AVAILABLE = 1
except ImportError:
    pass

STRATEGY = 'fixed'
BACKENDS = defaultdict(dict)

__all__ = ['STRATEGY', 'BACKENDS']


class MemoryBackend(BackendInterface):
    def __init__(self, config):
        super(MemoryBackend, self).__init__(config)
        self.memdict = defaultdict(lambda: {'count': 0, 'name': str})
        self.lock = Lock()

    def expire(self, eventname, abstime):
        self.lock.acquire()
        try:
            if self.memdict[eventname]['timestamp'] < abstime:
                del self.memdict[eventname]
        except KeyError:
            pass
        self.lock.release()

    def increment(self, eventname, timestamp, inc: int):
        self.lock.acquire()
        self.memdict[eventname]['timestamp'] = timestamp
        self.memdict[eventname]['count'] += inc
        self.lock.release()

    def count(self, eventname):
        self.lock.acquire()
        try:
            count = self.memdict[eventname]['count']
        except KeyError:
            count = 0
        self.lock.release()
        return count

    def check_allowed(self, eventname, limit, timespan, increment):
        # TODO: expire not touched events (stale)
        now = time.time()
        then = now - timespan
        self.expire(eventname, then)
        self.increment(eventname, now, inc=increment)
        count = self.count(eventname)
        return count <= limit, count


BACKENDS[STRATEGY]['memory'] = MemoryBackend


if REDIS_AVAILABLE:
    class RedisBackend(BackendInterface):
        def __init__(self, backendconfig):
            super(RedisBackend, self).__init__(backendconfig)
            self.redis_pool = RedisPooledConn(backendconfig)

        def increment(self, eventname, timespan, inc: int):
            eventname = self._fix_eventname(eventname)
            
            redisconn = self.redis_pool.get_conn()
            pipe = redisconn.pipeline()
            pipe.incr(eventname, amount=inc)

            # if input is a float first convert to timedelta
            # since default expire input handles integers
            if isinstance(timespan, float):
                timespan = timedelta(seconds=timespan)
            pipe.expire(eventname, timespan)
            res = pipe.execute()
            return res[0]

        def check_allowed(self, eventname, limit, timespan, increment):
            count = self.increment(eventname, timespan, inc=increment)
            return count <= limit, count

    BACKENDS[STRATEGY]['redis'] = RedisBackend


if AIOREDIS_AVAILABLE:
    class AIORedisBackend(BackendInterface):
        def __init__(self, backendconfig):
            super(AIORedisBackend, self).__init__(backendconfig)
            self.config = backendconfig
            self._redis = None

        @property
        async def redis(self):
            if not self._redis:
                self.logger.debug(f"Connect to redis: {self.config}")
                try:
                    loop = asyncio.get_running_loop()
                except AttributeError:
                    # python 3.6
                    loop = asyncio.get_event_loop()
                self.logger.debug(f"Got running loop...")
                self._redis = await aioredis.create_redis_pool(self.config, loop=loop)
            return self._redis

        async def increment(self, eventname, timespan, inc: int):
            eventname = self._fix_eventname(eventname)

            self.logger.debug("Connection ok... -> create pipeline")
            pipe = (await self.redis).pipeline()

            pipe.incrby(eventname, inc)

            # if input is a float first convert to timedelta
            # since default expire input handles integers
            if isinstance(timespan, float):
                timespan = timedelta(seconds=timespan)
                timespan = timespan.seconds
            elif isinstance(timespan, timedelta):
                timespan = timespan.seconds

            pipe.expire(eventname, timespan)
            self.logger.debug("Run pipeline...")
            res = await pipe.execute()
            self.logger.debug("After pipeline")
            return res[0]

        async def check_allowed(self, eventname, limit, timespan, increment):
            count = await self.increment(eventname, timespan, increment)
            return count <= limit, count

    BACKENDS[STRATEGY]['aioredis'] = AIORedisBackend


if SQL_EXTENSION_ENABLED:
    from sqlalchemy import Column, Integer, Unicode, BigInteger, Index
    from sqlalchemy.sql import and_
    metadata = DeclarativeBase.metadata

    class Event(DeclarativeBase):
        __tablename__ = 'fuglu_ratelimit_fixed'
        eventid = Column(BigInteger, primary_key=True)
        eventname = Column(Unicode(255), nullable=False)
        count = Column(Integer, nullable=False)
        timestamp = Column(Integer, nullable=False)
        __table_args__ = (
            Index('idx_eventname_fixed', 'eventname'),
            Index('idx_timestamp', 'timestamp'),
        )

    class SQLAlchemyBackend(BackendInterface):
        def __init__(self, backendconfig):
            super(SQLAlchemyBackend, self).__init__(backendconfig)
            self.session = get_session(backendconfig)
            metadata.create_all(bind=self.session.bind)

        def expire(self, eventname, abstime):
            self.session.query(Event).filter(
                and_(Event.eventname == eventname, Event.timestamp < abstime)
            ).delete()
            self.session.flush()

        def increment(self, eventname, timestamp, inc: int):
            event = Event()

            instance = self.session.query(Event).filter(Event.eventname == eventname).first()
            if instance is None:
                # if not exists - create
                event.eventname = eventname
                event.count = inc
                event.timestamp = int(timestamp)
                self.session.add(event)
            else:
                # if exists - increment
                instance.count = instance.count + inc
                instance.timestamp = int(timestamp)

            self.session.flush()

        def db_count(self, eventname):
            e = self.session.query(Event.count).filter(Event.eventname == eventname).first()
            if e is None:
                return 0
            return e.count

        def count(self, eventname, timespan, inc: int):
            now = time.time()
            then = now-timespan
            if then is None:
                then = int(time.time())

            self.expire(eventname, then)
            self.increment(eventname, now, inc=inc)
            return self.db_count(eventname)
            
        def check_allowed(self, eventname, limit, timespan, increment):
            eventname = self._fix_eventname(eventname)
            count = self.count(eventname, timespan, inc=increment)
            return count <= limit, count

    BACKENDS[STRATEGY]['sqlalchemy'] = SQLAlchemyBackend
