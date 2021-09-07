import json

from awesomeTaskPy.log.loger import loger
from awesomeTaskPy.queue.queue import queue
from awesomeTaskPy.context.systemEventRegister import systemEventRegister
import sys
contextObj=None
class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]
class context():
    __taskInfo = None
    __log = None
    __queue = None

    def __init__(self, taskInfo):
        if taskInfo is not None:
            self.__taskInfo = taskInfo
            self.__log = loger.instance(self.__taskInfo['taskId'])
            self.__queue=queue(taskInfo)
            self.__log.setQueue(self.__queue)
    def getTaskInfo(self):
        return self.__taskInfo

    def getLoger(self):
        return self.__log
    def getQueue(self):
        return self.__queue

def getContext():
    global contextObj
    if contextObj is None:
        contextObj=context(json.loads(sys.argv[1]))
    return contextObj
def initContext():
    global contextObj
    if contextObj!=None:
        return contextObj
    if len(sys.argv)>=2:
        taskInfo = json.loads(sys.argv[1])
        if not isinstance(taskInfo, dict):
            taskInfo = json.loads(taskInfo)
        contextObj = context(taskInfo)
        #注册系统事件  注意事件中最好不要有阻塞的处理
        # 由于事件的调用是在接受节点传输的线程中
        # 在此事件触发执行完成之前不会获取到节点返回的数据
        systemEventRegister.register()
    else:
        contextObj=context(None)
        raise Exception("context failed find taskInfo from command")
