import os
import shutil


def get_last_component(string: str):
    Broken = string.split('/')
    length = len(Broken)

    return Broken[length - 1]


def basePath(URL):
    if URL.endswith('/'):
        URL = URL[:-1]

    Broken = URL.split('/')
    length = len(Broken)

    LastItem = Broken[length - 1]
    NewPath = ''

    for path in Broken:
        Bad = [LastItem, '']

        continuee = False

        for b in Bad:
            if path == b:
                continuee = True

        if continuee:
            continue

        NewPath = NewPath + '/' + path

    return NewPath


def file_exists(path):
    return os.path.isfile(path)


def directory_exists(path):
    return os.path.isdir(path)


def os_walk(file_name, path):
    for r, d, f in os.walk(path):
        for file in f:
            if file == file_name:
                return os.path.abspath(os.path.join(r, file))


def copy(src, dst):
    if os.path.isdir(src):
        if dst.endswith('/'):
            dst = dst + get_last_component(src)
        elif not dst.endswith('/'):
            dst = dst + '/' + get_last_component(src)
        return shutil.copytree(src=src, dst=dst)
    else:
        return shutil.copy(src=src, dst=dst)


def join(path1: str, path2: str):
    if path1.endswith('/'):
        path1 = path1[:-1]

    if path2.endswith('/'):
        path2 = path2[:-1]

    if not path1.startswith('/'):
        path1 = '/' + path1

    if not path2.startswith('/'):
        path2 = '/' + path2

    path = path1 + path2
    return path


class PathObject:
    """
    -- PathObject --
    attempt to emulate the URL type in swift,
    allows for relatively similar functionality in pure python
    also allowing more flexibility and error corrections when joining or appending paths together
    """
    def __init__(self, path):
        path = str(path)
        if not path.startswith('/'):
            path = '/' + path

        path.replace(" ", "")

        self.path = path

    def append(self, new_path):
        self.path = join(self.path, new_path)

    def isPath(self):
        if file_exists(self.path) or directory_exists(self.path):
            return True
        else:
            return False

    def BasePath(self):
        return basePath(self.path)

    def last_component(self):
        return get_last_component(self.path)

    def strip_last(self):
        self.path = basePath(self.path)

    def write_to(self, WritingData, OpenMode):
        with open(self.path, OpenMode) as file:
            file.write(WritingData)

    def rename(self, name):
        src = self.path
        dst = join(basePath(self.path), '/' + name)
        os.rename(src=src, dst=dst)
        self.path = dst


if __name__ == '__main__':
    pass
