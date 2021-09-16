import sys
import os
import beniutils as b


def main():
    parList = sys.argv[1:]
    if parList:
        funcName = parList.pop(0)
        if funcName not in funcNameList:
            exit(f"非法命令名称 {funcName}", True)
        func = eval(funcName)
        func(*parList)
    else:
        # 没有输入命令
        exit(None, True)


helpInfo = '''

beniutils task_create <target_path>
创建beniutils.task项目（如果不传入目标路径则在当前系统路径下进行）

beniutils task_build <target_path>
发布beniutils.task项目（如果不传入目标路径则在当前系统路径下进行）
    
'''

funcNameList = [
    "task_create",
    "task_build",
]


def task_create(targetPath=None):
    targetPath = targetPath or os.getcwd()
    b.makeFolder(targetPath)
    workspaceFolder = b.getTempWorkspace()
    try:
        taskCreateZipFile = b.getPath(os.path.dirname(__file__), "data/task_create.zip")
        b.zipFileExtract(taskCreateZipFile, workspaceFolder)
        for fileName in os.listdir(workspaceFolder):
            toFile = b.getPath(targetPath, fileName)
            if os.path.exists(toFile):
                raise Exception(f"创建失败，指定路径下已存在 {toFile}")
        for fileName in os.listdir(workspaceFolder):
            fromFile = b.getPath(workspaceFolder, fileName)
            toFile = b.getPath(targetPath, fileName)
            b.copy(fromFile, toFile)
        print("创建项目成功 " + targetPath)
    finally:
        b.remove(workspaceFolder)


def task_build(targetPath=None):
    try:
        ignoreList = ["main.py", "main_config.py", ]
        currentPath = os.getcwd()
        targetPath = targetPath or currentPath
        workspaceFolder = b.getTempWorkspace()
        mainPyFile = b.getPath(targetPath, "project/src/main.py")
        if not os.path.isfile(mainPyFile):
            exit(f"发布失败，主文件不存在 {mainPyFile}")
        hiddenimports = [x[:-3] for x in os.listdir(os.path.dirname(mainPyFile)) if x.endswith(".py") and x not in ignoreList]
        name = "task"
        icon = b.getPath(workspaceFolder, "task.ico")
        pathex = b.getPath(targetPath, "project")
        taskBuildZipFile = b.getPath(os.path.dirname(__file__), "data/task_build.zip")
        b.zipFileExtract(taskBuildZipFile, workspaceFolder)
        taskSpecFile = b.getPath(workspaceFolder, "task.spec")
        taskSpecContent = b.readFile(taskSpecFile)
        taskSpecContent = taskSpecContent.replace("<<mainPyFile>>", mainPyFile)
        taskSpecContent = taskSpecContent.replace("<<pathex>>", pathex)
        taskSpecContent = taskSpecContent.replace("<<hiddenimports>>", ",".join([f'"{x}"' for x in hiddenimports]))
        taskSpecContent = taskSpecContent.replace("<<name>>", name)
        taskSpecContent = taskSpecContent.replace("<<icon>>", icon)
        b.writeFile(taskSpecFile, taskSpecContent)
        # import PyInstaller.__main__
        # sys.argv = ["", taskSpecFile]
        # PyInstaller.__main__.run() # pyinstaller main.py -F
        os.chdir(workspaceFolder)
        _returncode, outBytes, errBytes = b.execute(f"pyinstaller {taskSpecFile}", ignoreError=True)

        outStr = b.decode(outBytes).replace("\r\n", "\n")
        errStr = b.decode(errBytes).replace("\r\n", "\n")
        executeLog = "\n".join([outStr, errStr])
        print(executeLog)

        fromExeFile = b.getPath(workspaceFolder, f"dist/{name}.exe")
        toExeFile = b.getPath(targetPath, "project/bin/" + os.path.basename(fromExeFile))
        if not os.path.exists(fromExeFile):
            exit("生成exe文件失败")
        b.remove(toExeFile)
        b.copy(fromExeFile, toExeFile)
    finally:
        os.chdir(currentPath)
        b.remove(workspaceFolder)


def exit(errorMsg, isShowHelpInfo=False):
    if errorMsg:
        print(errorMsg)
    if isShowHelpInfo:
        print(helpInfo)
    sys.exit(errorMsg and 1 or 0)
