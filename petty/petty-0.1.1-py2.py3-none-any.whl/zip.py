# zip模块
import io
import os
import zipfile


class Zip:

    def __init__(self, zipfile_path):
        self.name = zipfile_path
        if os.path.exists(zipfile_path):
            with open(zipfile_path, mode='rb') as f:
                self.data = io.BytesIO(f.read())
                self.pzip = zipfile.ZipFile(self.data)
        else:
            zf = zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED)
            zf.close()
            with open(zipfile_path, mode='rb') as f:
                self.data = io.BytesIO(f.read())
                self.pzip = zipfile.ZipFile(self.data)

    def close(self):
        self.pzip.close()

    def getinfo(self, name):
        return self.pzip.getinfo(name)

    def infolist(self):
        return self.pzip.infolist()

    def namelist(self):
        return self.pzip.namelist()

    def open(self, name, mode='r', pwd=None):
        return self.pzip.open(name, mode='r', pwd=None)

    def extract(self, member, path=None, pwd=None):
        return self.pzip.extract(member, path=None, pwd=None)

    def extractall(self, path=None, members=None, pwd=None):
        return self.pzip.extractall(path=None, members=None, pwd=None)

    def printdir(self):
        return self.pzip.printdir()

    def setpassword(self, pwd):
        return self.pzip.setpassword(pwd)

    def read(self, name, pwd=None):
        return self.pzip.read(name, pwd=None)

    def add(self, arcname, filepath):
        """往zip文件中，添加文件

        Args:
            arcname (str): zip中的文件名
            filepath (str): 文件路径
        """
        with open(filepath, 'rb') as f:
            fdata = f.read()

        mzip = io.BytesIO()
        zout = zipfile.ZipFile(mzip, mode="w")
        for item in self.pzip.infolist():
            data = self.pzip.read(item.filename)
            if item.filename != arcname:
                zout.writestr(item, data)

        zout.writestr(arcname, fdata)
        zout.close()

        self.data = mzip
        self.pzip = zipfile.ZipFile(self.data)

    def delete(self, arcname):
        """删除zip文件中的文件

        Args:
            arcname (str): 文件路径
        """
        mzip = io.BytesIO()
        zout = zipfile.ZipFile(mzip, mode="w")
        for item in self.pzip.infolist():
            data = self.pzip.read(item.filename)
            if item.filename != arcname:
                zout.writestr(item, data)

        zout.close()

        self.data = mzip
        self.pzip = zipfile.ZipFile(self.data)

    def save(self, filename):
        """将修改后的zip文件，保存起来

        Args:
            filename (str): 保存后的文件名/路径
        """
        pzip = zipfile.ZipFile(self.data)
        zout = zipfile.ZipFile(filename, 'w')
        for item in pzip.infolist():
            dat = pzip.read(item.filename)
            zout.writestr(item, dat)
        zout.close()
