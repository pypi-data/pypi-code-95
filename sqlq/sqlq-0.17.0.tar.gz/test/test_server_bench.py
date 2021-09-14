from sqlq import *
import asyncio
import threadwrapper


async def sql(j, loop, result, key):
    a = sqlqueue.sql("INSERT INTO `test` VALUES (?);", (j,), result=result, key=key)
    return a


async def _sql(j, loop, result, key):
    result[key] = sqlqueue._sql(id(j), "INSERT INTO `test` VALUES (?);", (j,))


async def sql_async(j, loop, result, key):
    sqlqueue.sql_async("INSERT INTO `test` VALUES (?);", (j,), result=result, key=key)


async def _sql_async(j, loop, result, key):
    result[key] = await sqlqueue._sql_async(id(j), "INSERT INTO `test` VALUES (?);", (j,), loop=loop)


sqlqueue = SqlQueueU(server=True, db=r"db.db", depth=2, timeout_backup=10000, auto_backup=True)
for func in [_sql, _sql_async, sql, sql_async]:
    for j in [1,2**5,2**6,2**7,2**8,2**9]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        twa = threadwrapper.ThreadWrapper_async(asyncio.Semaphore(2**9), loop)
        result = {-1: 0}
        sqlqueue.sql("DELETE FROM `test`;")
        sqlqueue.commit()
        start = time.time()
        for i in range(j):
            twa.add(func(i, loop, result, i))
        twa.wait()
        sqlqueue.commit()
        elapsed = time.time()-start
        print("{:<20}{:>6} {:>6.2f}s {:>10.2f} sqls/sec".format(func.__name__+"()", j, elapsed, j/elapsed))
        if j == 1:
            print(result)
        loop.stop()
sqlqueue.stop()
