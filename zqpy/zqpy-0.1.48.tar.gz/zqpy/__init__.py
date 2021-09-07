print(" Init zqpy core By ZhouQing")

import os, sys, json
sys.path.append(os.path.dirname(__file__))

from .LogService import LogServiceClass
from .FileService import FileServiceClass
from .HttpService import HttpServiceClass
from .RegexService import RegexServiceClass
from .ThreadService import ThreadServiceClass
from .TimeService import TimeServiceClass
from .VideoDownloadService import VideoDownloadServiceClass
from .LocallizeService import LocallizeServiceClass
from .WaitExecutService import WaitExecutServiceClass
from .QrCodeService import QrCodeServiceClass
from .ToolsService import ToolsServiceClass
from .MailService import MailServiceClass
from .ADBService import *
from .SqliteService import SqliteServiceClass
from .AIService import AIServiceClass
from .ProxyServer import ProxyServerClass, ProxySourceType
from .ZipService import ZipServiceClass
from .APSchedulerService import APSchedulerServiceClass
from .ExcelService import ExcelServiceClass
from .ImageEditorService import ImageEditorServiceClass
from .VideoEditorService import VideoEditorServiceClass

def OpenAutoInstall():
    from .AutoInstall import AutoInstallClass# 自动导入缺失的库

LogTag = "zqpy"

def vLocallizePath():
    return None

Log = LogServiceClass(tag=LogTag)
LogD = Log.LogD
LogW = Log.LogW
LogE = Log.LogE
FileService = FileServiceClass()
HttpService = HttpServiceClass()
RegexService = RegexServiceClass()
ThreadService = ThreadServiceClass()
TimeService = TimeServiceClass()
VideoDownloadService = VideoDownloadServiceClass()
LocalizeService = LocallizeServiceClass(path=(vLocallizePath() or None))
WaitExecutService = WaitExecutServiceClass()
QrCodeService = QrCodeServiceClass()
ToolsService = ToolsServiceClass()
MailService = MailServiceClass()
ADBService = ADBServiceClass()
SqliteService = SqliteServiceClass()
ZipService = ZipServiceClass()
APSchedulerService = APSchedulerServiceClass()
ExcelService = ExcelServiceClass()
ImageEditorService = ImageEditorServiceClass()
VideoEditorService = VideoEditorServiceClass()
ProxyServer = ProxyServerClass()

AIService = AIServiceClass()

########################################通用方法##########################################
def GetLocalize(key):
    return LocalizeService.Get(key)

############################################子类可重写##########################################