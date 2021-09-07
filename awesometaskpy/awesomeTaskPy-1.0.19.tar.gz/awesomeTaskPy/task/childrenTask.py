from datetime import datetime
from awesomeTaskPy.context.event import event
import time

class childrenTask:
    __statusMap = {
        "wait":'wait',
        'running':'running',
        'success':'success',
        'error':'error'
    }
    __rpcInfo = None
    __childrenTaskId = None
    __forkAt = None
    __runAt = None
    __endAt = None
    __status = None
    __input = None
    __result = None
    __error = None
    def __init__(self,rpcInfo):
        self.__childrenTaskId = rpcInfo['taskId']
        self.__forkAt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__status = self.__statusMap['wait']
        self.__input = rpcInfo['input']
        def callBack(params):
            params = params['content']
            if 'error' in params.keys():
                self.__status = self.__statusMap['error']
                self.__error = params['error']
            else:
                self.__status = self.__statusMap['success']
            self.__result = params['result']
            self.__runAt = params['startAt']
            self.__endAt = params['endAt']
        event.register(self.__childrenTaskId,callBack)
    def getResult(self,timeOut = 300,awaitTime = 0.1):
        nowInt = int(time.time())
        while (int(time.time()) - nowInt)<timeOut:
            if self.__status!=self.__statusMap["wait"]:
                if self.__result is not None:
                    return self.__result
                else:
                    raise Exception(self.__error)
            else:
                time.sleep(awaitTime)

        raise Exception("remote apply failed cause timeout wait time:"+str(int(time.time()) - nowInt))
