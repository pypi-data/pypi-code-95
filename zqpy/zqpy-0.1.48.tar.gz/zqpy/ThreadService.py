import threading
import inspect
import ctypes

class ThreadServiceClass(object):
    def __init__(self):
        self.threadDic = {}

    def AddThread(self, Target, IsImmRun, Name = ""):
        '''
        IsImmRun:是否立即运行
        '''
        if Target == None:
            return None
        id = len(self.threadDic)
        self.threadDic[id] = ThreadItemClass(Name,Target,IsImmRun,Id=id)
        return self.threadDic[id]
    
    def RomeThread(self, ThreadItemClass):
        if ThreadItemClass == None:
            return
        if ThreadItemClass.ThreadId in self.threadDic:
            self.threadDic.pop(ThreadItemClass.ThreadId)

    def GetThread(self, ThreadItemClass):
        if ThreadItemClass == None:
            return None
        self.threadDic.get(ThreadItemClass.ThreadId, None)
        
    def GetThreadById(self, ThreadId):
        self.threadDic.get(ThreadId, None)
        
    def GetThreadByName(self, Name):
        listThread = None
        for item in self.threadDic:
            if self.threadDic[item].ThreadName == Name:
                if not listThread:
                    listThread = []
                listThread.append(self.threadDic[item])
        return listThread

    def GetThreadCount(self):
        return len(self.threadDic)

    '''
    def ReRunAll(self):
        for itemThread in self.threadDic:
            threadItem = self.threadDic[itemThread]
            if threadItem :
                threadItem.Run()
    '''

class ThreadItemClass(object):
    def __init__(self, Name, Target, IsImmRun, Id = 0):
        self.ThreadName = Name
        self.ThreadId = Id
        self.Target = Target
        self.ThreadInstance = threading.Thread(name=Name, target=Target)
        self.lock = None
        if IsImmRun:
            self.Start()

    def Start(self):
        self.ThreadInstance.start()
        
    def Run(self, isKillRun = True):
        if self.ThreadInstance.isAlive():
            if isKillRun:
                self.Stop()
                self.ThreadInstance = threading.Thread(name=self.ThreadName, target=self.Target)
                self.Start()
        else:
            self.Start()

    def Stop(self):
        if not self.ThreadInstance:
            return
        self.ThreadInstance._stop()
        '''
        tid = self.ThreadInstance.ident
        exctype = SystemExit
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
        '''
    
    def Lock(self):
        self.lock = threading.Lock()
        
    def UnLock(self):
        if self.lock:
            self.lock.acquire()
            self.lock.release()

    def ChangeTarget(self, Target):
        self.ThreadInstance._target = Target

def Target():
    i = 0
    while i < 10:
        i += 1
        print(i)

if __name__ == "__main__":
    ThreadService = ThreadServiceClass()
    A = ThreadService.AddThread(Target, True, "dsda")
    B = ThreadService.AddThread(Target, True, "dsda1")
    # A.Lock()
    # A.UnLock()
    B.Run()
    B.Run()
    B.Run()