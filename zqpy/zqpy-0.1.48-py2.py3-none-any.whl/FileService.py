import os, hashlib
from natsort import natsorted
from shutil import copyfile

class FileServiceClass(object):
    def __init__(self):
        pass
    
    def AppendFile(self, filePath, content, isEnter = False):
        currDirName = os.path.dirname(filePath)
        if not os.path.exists(currDirName):
            os.makedirs(currDirName)
        fd = os.open(filePath,os.O_RDWR|os.O_APPEND|os.O_CREAT)
        os.write(fd,bytes(content + ("\n" if isEnter else ""), encoding='utf-8'))
        os.close(fd)

    def WriteFile(self, filePath, content, isEnter = False):
        currDirName = os.path.dirname(filePath)
        if not os.path.exists(currDirName):
            os.makedirs(currDirName)
        fd = os.open(filePath,os.O_RDWR|os.O_CREAT)
        os.write(fd,bytes(content + ("\n" if isEnter else ""), encoding='utf-8'))
        os.close(fd)

    def ReadFile(self, filePath, encoding = "utf-8"):
        configFs = open(filePath,"r+",encoding = encoding)
        configContent = configFs.read()
        return configContent

    def Exists(self, filePath):
        return os.path.exists(filePath)
    
    def GetFiles(self, dirPath, isCurrDir, excludeList = []):
        filesTemp = []
        for root, dirs, files in os.walk(dirPath):
            for filePath in files:
                isAppend = False
                if isCurrDir:
                    if root == dirPath:
                        isAppend = True
                else:
                    isAppend = True
                if isAppend and not filePath in excludeList:
                    filesTemp.append(os.path.join(root, filePath))
            if isCurrDir and root == dirPath:
                break
        return filesTemp
    
    def GetDirs(self,dirPath, isCurrDir, excludeList = []):
        dirsTemp = []
        for root, dirs, files in os.walk(dirPath):
            for dir in dirs:
                isAppend = False
                if isCurrDir:
                    if root == dirPath:
                        isAppend = True
                else:
                    isAppend = True
                if isAppend and not dir in excludeList:
                    dirsTemp.append(os.path.join(root, dir))
            if isCurrDir and root == dirPath:
                break
        return dirsTemp
    
    def CopyFile(self, sourceFile, targetFile, isAutoCreateDir = True):
        try:
            dirName = os.path.dirname(targetFile)
            if not os.path.exists(dirName) and isAutoCreateDir:
                os.makedirs(dirName)
            copyfile(sourceFile, targetFile)
            return True
        except IOError as e:
            print('CopyFile Error %s'%(str(e)))
            return False

    def GetFileMd5(self, filePath):
        if not os.path.isfile(filePath):
            return None
        myhash = hashlib.md5()
        f = open(filePath,'rb')
        while True:
            b = f.read(8096)
            if not b :
                break
            myhash.update(b)
        f.close()
        return myhash.hexdigest()

    def ShortFiles(self, fileList):
        return natsorted(fileList)

    def SpliteContentKV(self, path, spliteStr = "="):
        # spliteStrs 按照前后顺序切，也就是切出来是 表中表
        content = self.ReadFile(path)
        linesContent = content.splitlines()
        contents = {}
        for line in linesContent:
            splites = line.split(spliteStr, 1)
            contents.setdefault(splites[0].strip(),splites[1].strip())
        return contents
    
    def CreateDir(self, path):
        if path == "":
            return
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
    
    def ConvertTempPath(self, path:str):
        if path.startswith('./'):
            path = path[2:]
        elif path[1] == ":":
            path = path[3:-1]
        elif path.startswith('/'):
            path = path[1:-1]
        return "%s/zqpyTemp/%s"%(os.getenv("SystemDrive"), os.path.split(path)[1])

    def ConvertConfigPath(self, path:str):
        if path.startswith('./'):
            path = path[2:]
        elif path[1] == ":":
            path = path[3:-1]
        elif path.startswith('/'):
            path = path[1:-1]
        return "%s/zqpyConfig/%s"%(os.getenv("SystemDrive"), os.path.split(path)[1])

    def ConvertDataPath(self, path:str):
        if path.startswith('./'):
            path = path[2:]
        elif path[1] == ":":
            path = path[3:-1]
        elif path.startswith('/'):
            path = path[1:-1]
        return "%s/zqpyData/%s"%(os.getenv("SystemDrive"), os.path.split(path)[1])

    def CopyDirs(self, sourceDir, targetDir):
        print("当前处理文件夹 %s -> %s" %(sourceDir, targetDir))
        for f in os.listdir(sourceDir):
            sourceF = os.path.join(sourceDir, f)
            targetF = os.path.join(targetDir, f)
            if os.path.isfile(sourceF):
                #创建目录
                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)
                #文件不存在，或者存在但是大小不同，覆盖
                if not os.path.exists(targetF) or (os.path.exists(targetF) and (self.GetFileMd5(targetF) != self.GetFileMd5(sourceF))):
                    #2进制文件
                    open(targetF, "wb").write(open(sourceF, "rb").read())
                    print (u"%s 复制完毕" %(targetF))
                else:
                    print (u"%s 已存在，不重复复制" %(targetF))
            if os.path.isdir(sourceF):
                self.CopyDirs(sourceF, targetF)
                
if __name__ == "__main__":
    print(FileServiceClass().SpliteContentKV("Locallize.txt","="))