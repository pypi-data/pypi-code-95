import os

class FileWrapper:
    def __init__(self, fd, callback) -> None:
        self.fd = fd
        self.callback = callback
        self.length = os.fstat(fd.fileno()).st_size
    
    def __len__(self):
        return self.length
    
    def read(self, length=-1):
        result = self.fd.read(length)
        self.callback(len(result))
        return result