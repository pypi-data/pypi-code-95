import logging
import os
from datetime import datetime


class LogUtils():
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    time = datetime.now()
    date = time.strftime('%Y-%m-%d')

    def __init__(self):
        self.create_txt()

    def setLog(self,level,handler):
        self.logger.setLevel(level)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def removeLog(self,handler):
        self.logger.removeHandler(handler)

    def create_txt(self):
        #当前路径
        file_name = os.path.abspath(os.path.dirname(__file__))+"\\log\\"+self.date+".log"
        if not os.path.exists(file_name):
            # windows系统创建文件
            if os.name == "nt":
                fp = open(file_name,'wb')
                fp.close()
            # unix/OS X系统创建文件
            else:
                os.mknod(file_name)

    #输出错误信息到日志文件(error_msg写明哪个步骤出错,exception为捕获的异常)
    def error_msg(self,error_msg,exception):
        file_log = os.path.abspath(os.path.dirname(__file__))+"\\log\\"+self.date+".log"
        fileHandler = logging.FileHandler(file_log, mode='a', encoding='utf-8')
        self.setLog(logging.ERROR,fileHandler)
        self.logger.error(error_msg + '，' + exception)
        self.removeLog(fileHandler)

    #控制台打印正常输出
    def info_msg(self,info_msg):
        file_log = os.path.abspath(os.path.dirname(__file__)) + "\\log\\" + self.date + ".log"
        fileHandler = logging.FileHandler(file_log, mode='a', encoding='utf-8')
        self.setLog(logging.INFO, fileHandler)
        self.logger.info(info_msg)
        self.removeLog(fileHandler)
