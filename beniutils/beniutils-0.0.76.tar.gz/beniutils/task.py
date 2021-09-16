import os
import sys
import time

import beniutils as b
import beniutils.print_color as printcolor

workspacePath = None


def init(wPath):
    global workspacePath
    workspacePath = wPath


def getPathByWorkspace(*parList):
    return b.getPath(workspacePath, *parList)


def runFile(file):
    isException = False
    try:
        fileContent = b.readFile(file)
        findStr = ":: ---------------------------------------- ::"
        startIndex = fileContent.index(findStr)
        endIndex = fileContent.index(findStr, startIndex + 1)
        content = fileContent[startIndex + len(findStr):endIndex].strip().replace("\r\n", "\n")
        lineAry = content.split("\n")
        lineAry = [x[2:].strip() for x in lineAry]
        taskList = []
        for line in lineAry:
            sepIndex = line.find(" ")
            if sepIndex > -1:
                moduleName = line[:sepIndex].strip()
                parDict = eval(line[sepIndex:])
                assert type(parDict) == dict, f"参数无法解析成字典类型 line={line}"
            else:
                moduleName = line
                parDict = {}
            taskList.append([moduleName, parDict])
        assert len(taskList) > 0
        os.system(f"title={b.getFileBaseName(file)}")
    except:
        isException = True
        import traceback
        setPrintRedColor()
        traceback.print_exc()
        print("解析执行文件失败")
    finally:
        printcolor.resetColor()
    if not isException:
        runList(*taskList)


# [[moduleName, parDict], ...]
def runList(*taskList):
    lockFile = checkLockFile()
    try:
        logFolder = b.getPath(workspacePath, "log")
        b.makeFolder(logFolder)
        for logFile in sorted(b.getAllFileList(logFolder), reverse=True)[100:]:
            b.remove(logFile)
        logFile = b.getPath(logFolder, f"{time.strftime('%Y%m%d_%H%M%S')}.log")
        b.initLogger(logFile=logFile)
        for moduleName, *parList in taskList:
            parDict = parList and parList[0] or {}
            run(moduleName, **parDict)
    except Exception:
        import traceback
        setPrintRedColor()
        traceback.print_exc()
        b.error("执行失败")
    finally:
        printcolor.resetColor()
        b.info("任务结束")
        b.remove(lockFile)
        if not isDev():
            while True:
                time.sleep(1)


def run(moduleName, **parDict):
    exec(f"import {moduleName}")
    module = eval(moduleName)
    try:
        for k, v in parDict.items():
            if hasattr(module, k):
                setattr(module, k, v)
            else:
                b.warning(f"模块缺少属性定义 module={moduleName} k={k} v={v}")
        module.run()
    except Exception as e:
        raise e
    finally:
        if hasattr(module, "clean"):
            module.clean()


def initParDict():
    ary = sys.argv
    if len(ary) < 2:
        raise Exception("执行异常，参数长度小于2")
    moduleName = ary[1]
    parList = ary[2:]
    parDict = {}
    index = 0
    while index < len(parList):
        par = parList[index]
        if par.startswith("--"):
            index += 1
            try:
                parValue = parList[index]
            except:
                parValue = None
            parName = par[2:]
            if parName in parDict:
                raise Exception("发现有重复参数名")
            parDict[parName] = parValue
        index += 1
    return moduleName, parDict


def isDev():
    return sys.executable.endswith("python.exe")


def checkLockFile():
    lockFile = b.getPath(workspacePath, "task.lock")
    if os.path.isfile(lockFile):
        if isDev():
            print(f"不支持重复执行 {lockFile}")
            b.hold("当前调试模式下，输入unlock可继续：", True, "unlock")
        else:
            raise Exception(f"不支持重复执行 {lockFile}")
    b.writeFile(lockFile, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return lockFile


def setPrintRedColor():
    printcolor.set_cmd_text_color(printcolor.FOREGROUND_DARKRED)
