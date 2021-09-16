import asyncio
import binascii
import getpass
import gzip
import hashlib
import http.cookiejar
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import time
import urllib

import aiohttp
import chardet

_loggerName = 'beniutils'


def initLogger(loggerName=None, loggerLevel=None, logFile=None):
    LOGGER_FORMAT = '%(asctime)s %(levelname)-1s %(message)s', '%Y-%m-%d %H:%M:%S'
    LOGGER_LEVEL = loggerLevel or logging.INFO
    LOGGER_LEVEL_NAME = {
        logging.DEBUG: 'D',
        logging.INFO: '',
        logging.WARNING: 'W',
        logging.ERROR: 'E',
        logging.CRITICAL: 'C',
    }

    if loggerName:
        global _loggerName
        _loggerName = loggerName

    logger = logging.getLogger(_loggerName)
    logger.setLevel(LOGGER_LEVEL)
    for loggingLevel, value in LOGGER_LEVEL_NAME.items():
        logging.addLevelName(loggingLevel, value)

    loggerFormatter = logging.Formatter(*LOGGER_FORMAT)

    loggerHandler = logging.StreamHandler()
    loggerHandler.setFormatter(loggerFormatter)
    loggerHandler.setLevel(LOGGER_LEVEL)
    logger.addHandler(loggerHandler)

    if logFile:
        makeFolder(os.path.dirname(logFile))
        fileLoggerHandler = logging.FileHandler(logFile)
        fileLoggerHandler.setFormatter(loggerFormatter)
        fileLoggerHandler.setLevel(LOGGER_LEVEL)
        logger.addHandler(fileLoggerHandler)


def debug(msg, *args, **kwargs):
    logging.getLogger(_loggerName).debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    logging.getLogger(_loggerName).info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    logging.getLogger(_loggerName).warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logging.getLogger(_loggerName).error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    logging.getLogger(_loggerName).critical(msg, *args, **kwargs)


def openWindowsFolder(folder):
    os.system(f"start explorer {folder}")


def getPath(basePath, *parList):
    return os.path.abspath(os.path.join(basePath, *parList))


def writeFile(file, data, encoding='utf8', newline='\n'):
    makeFolder(os.path.dirname(file))
    with open(file, 'w', encoding=encoding, newline=newline) as f:
        f.write(data)
        f.flush()
        f.close()
    return file


def writeBinFile(file, data):
    makeFolder(os.path.dirname(file))
    with open(file, 'wb') as f:
        f.write(data)
        f.flush()
        f.close()
    return file


def readFile(file, encoding='utf8', newline='\n'):
    with open(file, 'r', encoding=encoding, newline=newline) as f:
        data = f.read()
        f.close()
    return data


def readBinFile(file):
    with open(file, 'rb') as f:
        data = f.read()
        f.close()
    return data


def jsonDumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def remove(fileOrFolder):
    if os.path.isfile(fileOrFolder):
        os.remove(fileOrFolder)
    elif os.path.isdir(fileOrFolder):
        shutil.rmtree(fileOrFolder)


def makeFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def clearFolder(*folderAry):
    for folder in folderAry:
        if os.path.isdir(folder):
            for target in getFileAndFolderList(folder):
                remove(target)


def copy(fromFileOrFolder, toFileOrFolder):
    if os.path.isfile(fromFileOrFolder):
        fromFile = fromFileOrFolder
        toFile = toFileOrFolder
        makeFolder(getParentFolder(toFile))
        shutil.copyfile(fromFile, toFile)
    elif os.path.isdir(fromFileOrFolder):
        fromFolder = fromFileOrFolder
        toFolder = toFileOrFolder
        makeFolder(getParentFolder(toFolder))
        shutil.copytree(fromFolder, toFolder)


def getParentFolder(fileOrFolder, level=1):
    result = fileOrFolder
    while level > 0:
        level -= 1
        result = os.path.dirname(result)
    return result


def getFileExtName(file):
    return file[file.rfind('.') + 1:].lower()


def getFileBaseName(file):
    fileName = os.path.basename(file)
    return fileName[:fileName.rfind(".")]


def getFileList(folder):
    ary = []
    for targetName in os.listdir(folder):
        target = os.path.join(folder, targetName)
        if os.path.isfile(target):
            ary.append(target)
    return ary


def getFolderList(folder):
    ary = []
    for targetName in os.listdir(folder):
        target = os.path.join(folder, targetName)
        if os.path.isdir(target):
            ary.append(target)
    return ary


def getFileAndFolderList(folder):
    ary = []
    for targetName in os.listdir(folder):
        target = os.path.join(folder, targetName)
        ary.append(target)
    return ary


def getAllFileList(folder):
    ary = []
    for targetName in getFileAndFolderList(folder):
        target = os.path.join(folder, targetName)
        if os.path.isfile(target):
            ary.append(target)
        elif os.path.isdir(target):
            ary.extend(getAllFileList(target))
    return ary


def getAllFolderList(folder):
    ary = []
    for targetName in getFileAndFolderList(folder):
        target = os.path.join(folder, targetName)
        if os.path.isdir(target):
            ary.append(target)
            ary.extend(getAllFolderList(target))
    return ary


def getAllFileAndFolderList(folder):
    ary = []
    for targetName in getFileAndFolderList(folder):
        target = os.path.join(folder, targetName)
        if os.path.isfile(target):
            ary.append(target)
        elif os.path.isdir(target):
            ary.append(target)
            ary.extend(getAllFileAndFolderList(target))
    return ary


def getFileMD5(file):
    data = readBinFile(file)
    return hashlib.md5(data).hexdigest()


def getFileCRC(file):
    return getDataCRC(readBinFile(file))


def getContentCRC(content):
    return getDataCRC(content.encode())


def getDataCRC(data):
    return hex(binascii.crc32(data))[2:].zfill(8)


def getClassFullName(classItem):
    return getattr(classItem, '__module__') + '.' + getattr(classItem, '__name__')


def decode(value):
    data = chardet.detect(value)
    encoding = data["encoding"] or "utf8"
    return value.decode(encoding)


def getTempWorkspace(clearOneDayBefore=True):
    baseWorkspaceFoler = getPath(os.path.expanduser("~"), "beniutils.workspace")
    makeFolder(baseWorkspaceFoler)
    nowTime = int(time.time() * 10000000)
    if clearOneDayBefore:
        oneDayBeforeTime = nowTime - 24 * 60 * 60 * 10000000
        for folderName in os.listdir(baseWorkspaceFoler):
            if int(folderName) < oneDayBeforeTime:
                remove(getPath(baseWorkspaceFoler, folderName))
    for i in range(100):
        nowTime += i
        workspaceFolder = getPath(baseWorkspaceFoler, str(nowTime))
        if not os.path.exists(workspaceFolder):
            makeFolder(workspaceFolder)
            return workspaceFolder
    raise Exception("创建tempWorkspace目录失败")


def execute(*pars, showCmd=True, showOutput=False, ignoreError=False):
    cmd = ' '.join(pars)
    if showCmd:
        info(cmd)
    p = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    outBytes, errBytes = p.communicate()
    p.kill()
    if showOutput:
        outStr = decode(outBytes).replace("\r\n", "\n")
        errStr = decode(errBytes).replace("\r\n", "\n")
        if outStr:
            info(f"output:\n{outStr}")
        if errStr:
            info(f"error:\n{errStr}")
    if not ignoreError and p.returncode != 0:
        raise Exception("执行命令出错")
    return p.returncode, outBytes, errBytes


def executeWinScp(winscpExe, keyFile, server, commandAry, showCmd=True):
    logFile = getPath(pathlib.Path.home(), "executeWinScp.log")
    remove(logFile)
    ary = [
        'option batch abort',
        'option transfer binary',
        f'open sftp://{server} -privatekey={keyFile} -hostkey=*',
    ]
    ary += commandAry
    ary += [
        'close',
        'exit',
    ]
    # /console
    cmd = f'{winscpExe} /log={logFile} /loglevel=0 /command ' + ' '.join('"%s"' % x for x in ary)
    return execute(cmd, showCmd=showCmd)


def executeTry(*parList, output=None, error=None):
    _code, outputBytes, errorBytes = execute(*parList, showCmd=False, ignoreError=True)
    if type(output) == str:
        output = output.encode()
    if output and output not in outputBytes:
        raise Exception(f"命令执行失败：{' '.join(parList)}")
    if type(error) == str:
        error = error.encode()
    if error and error not in errorBytes:
        raise Exception(f"命令执行失败：{' '.join(parList)}")


def zipFile(toFile, fileFolderOrAry, rename=None):
    from zipfile import ZIP_DEFLATED, ZipFile
    makeFolder(os.path.dirname(toFile))
    ary = fileFolderOrAry
    if type(ary) != list:
        ary = [fileFolderOrAry]
    rename = rename or (lambda x: os.path.basename(x))
    with ZipFile(toFile, 'w', ZIP_DEFLATED) as f:
        for file in sorted(ary):
            fname = rename(file)
            f.write(file, fname)


def zipFileForFolder(toFile, folder, rename=None, filterFun=None):
    if not folder.endswith(os.path.sep):
        folder += os.path.sep
    rename = rename or (lambda x: x[len(folder):])
    ary = getAllFileAndFolderList(folder)
    if filterFun:
        ary = list(filter(filterFun, ary))
    zipFile(toFile, ary, rename)


def zipFileExtract(file, toFolder=None):
    from zipfile import ZipFile
    toFolder = toFolder or os.path.dirname(file)
    with ZipFile(file) as f:
        for subFile in sorted(f.namelist()):
            try:
                # zipfile 代码中指定了cp437，这里会导致中文乱码
                encodeSubFile = subFile.encode('cp437').decode('gbk')
            except:
                encodeSubFile = subFile
            toFile = os.path.join(toFolder, encodeSubFile)
            toFile = toFile.replace('/', os.path.sep)
            f.extract(subFile, toFolder)
            # 处理压缩包中的中文文件名在windows下乱码
            if subFile != encodeSubFile:
                os.renames(os.path.join(toFolder, subFile), toFile)


def syncFolder(fromFolder, toFolder):
    # 删除多余目录
    toSubFolderList = sorted(getAllFolderList(toFolder), reverse=True)
    for toSubFolder in toSubFolderList:
        fromSubFolder = os.path.join(fromFolder, toSubFolder[len(toFolder + os.path.sep):])
        if not os.path.isdir(fromSubFolder):
            remove(toSubFolder)
    # 删除多余文件
    toFileList = getAllFileList(toFolder)
    for toFile in toFileList:
        fromFile = os.path.join(fromFolder, toFile[len(toFolder + os.path.sep):])
        if not os.path.isfile(fromFile):
            remove(toFile)
    # 同步文件
    fromFileList = getAllFileList(fromFolder)
    for fromFile in fromFileList:
        toFile = os.path.join(toFolder, fromFile[len(fromFolder + os.path.sep):])
        if os.path.isfile(toFile):
            fromData = readBinFile(fromFile)
            toData = readBinFile(toFile)
            if fromData != toData:
                writeBinFile(toFile, fromData)
        else:
            remove(toFile)
            copy(fromFile, toFile)
    # 添加新增目录
    fromSubFolderList = sorted(getAllFolderList(fromFolder), reverse=True)
    for fromSubFolder in fromSubFolderList:
        toSubFolder = os.path.join(toFolder, fromSubFolder[len(fromFolder + os.path.sep):])
        if not os.path.isdir(toSubFolder):
            makeFolder(toSubFolder)


def sendMail(host, password, fromMail, toMailList, subject, content='', attachmentList=None):
    '''发送邮件 attachmentList格式为[(name, bytes), ...]'''

    import smtplib
    from email.header import Header
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    message = MIMEMultipart()
    message['From'] = fromMail
    message['To'] = ','.join(toMailList)
    message['Subject'] = Header(subject, 'utf-8')
    message.attach(MIMEText(content, 'plain', 'utf-8'))

    if attachmentList:
        for item in attachmentList:
            att = MIMEText(item[1], 'base64', 'utf-8')
            att['Content-Type'] = 'application/octet-stream'
            # att['Content-Disposition'] = 'attachment; filename="file.txt"'
            att.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', item[0]))
            message.attach(att)

    smtpObj = smtplib.SMTP_SSL()
    smtpObj.connect(host)
    smtpObj.login(fromMail, password)
    smtpObj.sendmail(fromMail, toMailList, message.as_string())


_DEFAULT_FMT = '%Y-%m-%d %H:%M:%S'


def timestampByStr(value, fmt=None):
    fmt = fmt or _DEFAULT_FMT
    return int(time.mktime(time.strptime(value, fmt)))


def strByTimestamp(timestamp=None, fmt=None):
    timestamp = timestamp or time.time()
    fmt = fmt or _DEFAULT_FMT
    ary = time.localtime(timestamp)
    return time.strftime(fmt, ary)


def hold(msg=None, showInput=True, *exitValueList):
    msg = msg or "测试暂停，输入exit可以退出"
    exitValueList = exitValueList or ["exit"]
    inputFunc = showInput and input or getpass.getpass
    while True:
        inputValue = inputFunc(f"{msg}：")
        if inputValue in exitValueList:
            return inputValue

# ---- http


_defaultHeader = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}


# Cookie
_cookie = http.cookiejar.CookieJar()
_cookieProc = urllib.request.HTTPCookieProcessor(_cookie)
_opener = urllib.request.build_opener(_cookieProc)
urllib.request.install_opener(_opener)


def _getHeaderByDefault(headers):
    result = dict(_defaultHeader)
    if headers:
        for key, value in headers.items():
            result[key] = value
    return result


def httpGet(url, headers=None, timeout=30, retry=3):
    method = 'GET'
    headers = _getHeaderByDefault(headers)
    result = None
    response = None
    currentTry = 0
    while currentTry < retry:
        currentTry += 1
        try:
            request = urllib.request.Request(url=url, headers=headers, method=method)
            response = urllib.request.urlopen(request, timeout=timeout)
            result = response.read()
            response.close()
            break
        except Exception:
            pass
    contentEncoding = response.headers.get('Content-Encoding')
    if contentEncoding == 'gzip':
        result = gzip.decompress(result)
    return result, response


def httpPost(url, data=None, headers=None, timeout=30, retry=3):
    method = 'POST'
    headers = _getHeaderByDefault(headers)
    postData = data
    if type(data) == dict:
        postData = urllib.parse.urlencode(data).encode()
    result = None
    response = None
    currentTry = 0
    while currentTry < retry:
        currentTry += 1
        try:
            request = urllib.request.Request(url=url, data=postData, headers=headers, method=method)
            response = urllib.request.urlopen(request, timeout=timeout)
            result = response.read()
            response.close()
            break
        except Exception:
            pass
    return result, response


_maxAsyncFileNum = 5000
_currentAsyncFileNum = 0
_waitAsyncFileTime = 0.5


def setAsyncFileMaxNum(value):
    global _maxAsyncFileNum
    _maxAsyncFileNum = value


def toFloat(value, default):
    result = default
    try:
        result = float(value)
    except:
        pass
    return result


def toInt(value, default):
    result = default
    try:
        result = int(value)
    except:
        pass
    return result


def getLimitedValue(value, minValue, maxValue):
    value = min(value, maxValue)
    value = max(value, minValue)
    return value


_xPar = "0123456789abcdefghijklmnopqrstuvwxyz"


def intToX(value):
    n = len(_xPar)
    return ((value == 0) and "0") or (intToX(value // n).lstrip("0") + _xPar[value % n])


def xToInt(value):
    return int(value, len(_xPar))


async def asyncAwait(*taskList):
    resultList = []
    for task in taskList:
        resultList.append(await task)
    return resultList


async def asyncWriteFile(file, data, encoding='utf8', newline='\n'):
    import aiofiles
    makeFolder(os.path.dirname(file))
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(_waitAsyncFileTime)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'w', encoding=encoding, newline=newline) as f:
        await f.write(data)
        await f.flush()
        await f.close()
    _currentAsyncFileNum -= 1


async def asyncWriteBinFile(file, data):
    import aiofiles
    makeFolder(os.path.dirname(file))
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(_waitAsyncFileTime)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'wb') as f:
        await f.write(data)
        await f.flush()
        await f.close()
    _currentAsyncFileNum -= 1


async def asyncReadFile(file, encoding='utf8', newline='\n'):
    import aiofiles
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(_waitAsyncFileTime)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'r', encoding=encoding, newline=newline) as f:
        data = await f.read()
        await f.close()
    _currentAsyncFileNum -= 1
    return data


async def asyncReadBinFile(file):
    import aiofiles
    global _currentAsyncFileNum
    while _currentAsyncFileNum > _maxAsyncFileNum:
        await asyncio.sleep(_waitAsyncFileTime)
    _currentAsyncFileNum += 1
    async with aiofiles.open(file, 'rb') as f:
        data = await f.read()
        await f.close()
    _currentAsyncFileNum -= 1
    return data


async def asyncOpenXlsx(file):
    import xlrd3
    data = await asyncReadBinFile(file)
    return xlrd3.open_workbook(file_contents=data, formatting_info=True)
    # 只提供了异步打开xlsx的方法，没有提供异步写入xlsx的方法，因为xlwt不支持


async def asyncGetFileMD5(file):
    data = await asyncReadBinFile(file)
    return hashlib.md5(data).hexdigest()


async def asyncGetFileCRC32(file):
    data = await asyncReadBinFile(file)
    return binascii.crc32(data)


async def asyncGetFileCRCHex(file):
    return hex(await asyncGetFileCRC32(file))[2:].zfill(8)


async def asyncExecute(*parList):
    # 注意：针对windows，版本是3.8以下需要使用asyncio.subprocess，在执行main之前就要执行
    # 注意：在3.7如果调用对aiohttp有异常报错
    # asyncio.set_event_loop_policy(
    #    asyncio.WindowsProactorEventLoopPolicy()
    # )

    proc = await asyncio.create_subprocess_shell(
        ' '.join(parList),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout, stderr


_maxAsyncHttpNum = 3
_currentAsyncHttpNum = 0
_waitAsyncHttpTime = 0.1


def setAsyncHttpMaxNum(value):
    global _maxAsyncHttpNum
    _maxAsyncHttpNum = value


async def asyncHttpGet(url, headers=None, timeout=30, retry=3):
    importAioHttp()
    global _currentAsyncHttpNum
    headers = _getHeaderByDefault(headers)
    result = None
    response = None
    currentTry = 0
    while _currentAsyncHttpNum >= _maxAsyncHttpNum:
        await asyncio.sleep(_waitAsyncHttpTime)
    _currentAsyncHttpNum += 1
    while currentTry < retry:
        currentTry += 1
        try:
            response = None
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    url,
                    headers=headers,
                    timeout=timeout,
                )
                result = await response.read()
                response.close()
                # await session.close()
                if not result:
                    continue
                break
        except Exception:
            if response:
                response.close()
            warning(f'async http get exception url={url} times={currentTry}')
    _currentAsyncHttpNum -= 1
    return result, response


async def asyncHttpPost(url, data=None, headers=None, timeout=30, retry=3):
    importAioHttp()
    global _currentAsyncHttpNum
    headers = _getHeaderByDefault(headers)
    result = None
    response = None
    currentTry = 0
    while _currentAsyncHttpNum >= _maxAsyncHttpNum:
        await asyncio.sleep(_waitAsyncHttpTime)
    _currentAsyncHttpNum += 1
    while currentTry < retry:
        currentTry += 1
        try:
            response = None
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    url,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                )
                result = await response.read()
                response.close()
                # await session.close()
                if not result:
                    continue
                break
        except Exception:
            if response:
                response.close()
            warning(f'async http get exception url={url} times={currentTry}')
    _currentAsyncHttpNum -= 1
    return result, response


async def asyncDownload(url, file):
    result, _response = await asyncHttpGet(url)
    await asyncWriteBinFile(file, result)


isImportAioHttp = True


def importAioHttp():

    global isImportAioHttp
    if isImportAioHttp:
        isImportAioHttp = False
    else:
        return

    from asyncio.proactor_events import _ProactorBasePipeTransport
    from functools import wraps

    # 尝试优化报错：RuntimeError: Event loop is closed

    def silence_event_loop_closed(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except RuntimeError as e:
                if str(e) != 'Event loop is closed':
                    raise
        return wrapper

    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

# def scrapy(urlList, parseFun, extendSettings=None):

#     from scrapy.crawler import CrawlerProcess
#     from scrapy.utils.log import get_scrapy_root_handler
#     import scrapy.http

#     resultList = []
#     resultUrlList = urlList[:]

#     class TempSpider(scrapy.Spider):

#         name = str(random.random())
#         start_urls = urlList

#         def parse(self, response):
#             itemList, urlList = parseFun(response)
#             if itemList:
#                 resultList.extend(itemList)
#             if urlList:
#                 for url in urlList:
#                     resultUrlList.append(url)
#                     yield scrapy.http.Request(url)

#     settings = {
#         'LOG_LEVEL': logging.INFO,
#         'LOG_FORMAT': '%(asctime)s %(levelname)-1s %(message)s',
#         'LOG_DATEFORMAT': '%Y-%m-%d %H:%M:%S',
#         'DOWNLOAD_TIMEOUT': 5,
#         'CONCURRENT_REQUESTS': 50,
#         'RETRY_HTTP_CODES': [514],
#         'RETRY_TIMES': 5,
#         # 'ITEM_PIPELINES': {
#         #    ptGetClassFullName( TempPipeline ): 300,
#         # },
#     }
#     if extendSettings:
#         for k, v in extendSettings.items():
#             settings[k] = v

#     process = CrawlerProcess(settings)
#     process.crawl(TempSpider)
#     process.start()

#     rootHandler = get_scrapy_root_handler()
#     if rootHandler:
#         rootHandler.close()

#     # 函数执行后再调用logging都会有2次显示在控制台
#     logging.getLogger().handlers = []

#     return resultList, resultUrlList
