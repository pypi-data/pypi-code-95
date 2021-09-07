# -*- coding: utf-8 -*-
from threading import Timer
import time

class WaitExecuteItemClass(object):
    id = -1
    currTime = 0
    nextTime = -1
    waitTime = -1
    repeatNum = 0
    funcEvent = None
    completeEvent = None
    killEvent = None

    isKill = False
    isFinish = False
    currRepeatNum = 1

    def run(self):
        if self.isFinish:
            return False
        if self.nextTime == -1:
            self.nextTime = self.waitTime
        if self.waitTime == 0:
            if self.funcEvent:
                self.funcEvent()
        else:
            if self.currTime == self.nextTime or self.nextTime == 0:
                if self.funcEvent:
                    self.funcEvent()
                if self.repeatNum == -1 or self.currRepeatNum < self.repeatNum:
                    self.nextTime = self.currTime + self.waitTime
                    self.currRepeatNum += 1
                else:
                    if self.completeEvent:
                        self.completeEvent()
                    self.isFinish = True
                    return False

        self.currTime += 1
        if self.isKill:
            self.killEvent()
            return False
        return True


    def stop(self):
        self.isKill = True


class WaitExecutServiceClass(object):
    waitDic = None
    mainTimer = None
    currIndex = 0

    def __init__(self, isOpen = False):
        self.waitDic = {}
        if isOpen:
            self.Open()

    def Open(self):
        self.mainTimer = Timer(1, self.run, args=())
        self.mainTimer.start()

    def Close(self):
        try:
            for key in self.waitDic.keys():
                self.RemoveWiteExecute(key)
            self.mainTimer._stop()
        except BaseException as e:
            print(str(e))
    
    def AddWaitExecute(self, repeatNum, waitTime, funcEvent, completeEvent, killEvent):
        self.currIndex += 1
        waitExecuteItem = WaitExecuteItemClass()
        waitExecuteItem.id = self.currIndex
        waitExecuteItem.waitTime = waitTime
        waitExecuteItem.repeatNum = repeatNum
        waitExecuteItem.funcEvent = funcEvent
        waitExecuteItem.completeEvent = completeEvent
        waitExecuteItem.killEvent = killEvent
        self.waitDic[self.currIndex] = waitExecuteItem
        return waitExecuteItem

    def RemoveWiteExecute(self, id):
        if self.waitDic and self.waitDic.get(id):
            self.waitDic[id].stop()

    def RemoveWiteExecute_item(self, waitExecuteItemData):
        if waitExecuteItemData:
            self.RemoveWiteExecute(waitExecuteItemData.id)

    def GetWaitExecute(self, id):
        if self.waitDic and self.waitDic.get(id):
            return self.waitDic[id]
        return None

    def run(self):
        index = 0
        while True:
            time.sleep(1)
            index += 1
            if len(self.waitDic) == 0:
                continue
            notNextDicKeys = []
            for item in self.waitDic:
                if self.waitDic:
                    isNextRun = self.waitDic[item].run()
                    if not isNextRun:
                        notNextDicKeys.append(item)
            for item in notNextDicKeys:
                self.waitDic.pop(item)

if __name__ == "__main__":
    waitExecute = WaitExecutServiceClass()
    waitExecute.Open()
    def funcEvent():
        print('funcEvent')
    def completeEvent():
        print('completeEvent')
    def killEvent():
        print('killEvent')
    waitExecute.AddWaitExecute(-1,0,funcEvent,completeEvent,killEvent)
    waitExecute.AddWaitExecute(-1,0,funcEvent,completeEvent,killEvent)

    import time
    time.sleep(4)
    waitExecute.Close()
