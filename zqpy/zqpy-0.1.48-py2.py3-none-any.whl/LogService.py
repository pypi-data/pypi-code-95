import time, os, pretty_errors, sys
from TimeService import TimeServiceClass
from FileService import FileServiceClass

class LogServiceClass(object):
    TimeService = TimeServiceClass()
    FileService = FileServiceClass()

    filePath = "{}{}-Common.log".format("./Log/",TimeService.GetPrintTimeToDay()) 
    tag = ""
    def __init__(self, filePath = None, tag = None):
        if filePath != None:
            self.filePath = filePath
        if tag != None:
            self.tag = tag
        self.FileService.AppendFile(self.filePath, "{}{} {} {}".format("\n", self.TimeService.GetPrintTimeToAll(), self.tag, "- Start \n\n"))
        
    # 打印日志
    def Log(self, content, type=0):
        front = "LogD"
        if type == 0:
            front = "LogD"
        elif type == 1:
            front = "LogW"
        elif type == 2:
            front = "LogE"
        outPrint = "{} {} {}: {}".format(self.TimeService.GetPrintTimeToAll(), self.tag, front, content)
        self.SavePrintToFile(outPrint)
        print(outPrint)

    def LogD(self, *content):
        self.Log(content, 0)

    def LogW(self, *content):
        self.Log(content, 1)

    def LogE(self, *content):
        self.Log(content, 2)

    def SavePrintToFile(self, content):
        if self.filePath:
            self.FileService.AppendFile(self.filePath, content, True)

    def LogProgressBar(self, portion, total, desc = ''):
        '''
        total 总数据大小，portion 已经传送的数据大小
        :param portion: 已经接收的数据量
        :param total: 总数据量
        :return: 接收数据完成，返回True
        '''
        part = total / 50  # 1%数据的大小
        count = int(portion / part)
        sys.stdout.write('\r')
        sys.stdout.write(desc+('[%-50s]%.2f%%' % (('>' * count), portion / total * 100)))
        sys.stdout.flush()

        if portion >= total:
            sys.stdout.write('\n')
            return True
            
    # 进度打印
    def LogProgress(self, curr, total, commonDesc, finishDesc):
        if curr == total:
            percent = 100.0
            print('%s : %s [%d/%d]'%(commonDesc, str(percent)+'%', curr, total), end='\n')
        else:
            percent = round(1.0 * curr / total * 100,2)
            print('%s : %s [%d/%d]'%(finishDesc, str(percent)+'%', curr, total), end='\r')

if __name__ == '__main__':
    LogService = LogServiceClass(tag="ADBServiceClass")
    LogService.Log(15)
    LogService.LogD(16,66)
    LogService.LogW(17)
    LogService.LogE(18)