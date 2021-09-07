from FileService import FileServiceClass
class LocallizeServiceClass(object):
    def __init__(self, path = None):
        self.File = FileServiceClass()
        self.localData = {}
        self.ChangeData(path)

    def ChangeData(self, path=None):
        if path != None:
            if not self.File.Exists(path):
                print("Not Locallize File ->  {}".format(path))
            else:
                self.localData = self.File.SpliteContentKV(path)
                
    def Get(self, key):
        return self.localData.get(key or "NoLocallize",'{}{}'.format(str(key)," 没有写入到文本"))