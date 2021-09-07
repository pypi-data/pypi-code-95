from contextlib import closing
import requests
import os
from LogService import LogServiceClass

class VideoDownloadServiceClass(object):
    Log = LogServiceClass(tag="VideoDownloadServiceClass")
    LogD = Log.LogD
    LogW = Log.LogW
    LogE = Log.LogE
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        # 'user-agent': 'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; MI 4S Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.146 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.1.3',
    }
    def __init__(self, *args):
        pass
    
    def Down(self, urlPath, saveFilePath):
        try:
            requests.adapters.DEFAULT_RETRIES = 5
            s = requests.session()
            s.keep_alive = False
            with closing(requests.get(urlPath, headers = self.headers, stream=True)) as response:
                if not response.ok:
                    print('错误页面：==>>>  ' + response.text)
                    return False, saveFilePath
                chunk_size = 1024
                content_size = int(response.headers['content-length'])
                if(os.path.exists(saveFilePath) and os.path.getsize(saveFilePath)==content_size):
                    print('跳过'+saveFilePath)
                    return False, saveFilePath
                else:
                    if not ".mp4" in saveFilePath.lower():
                        saveFilePath = saveFilePath + ".mp4" 
                    videoDirPath = os.path.dirname(saveFilePath)
                    if not os.path.exists(videoDirPath):
                        os.makedirs(videoDirPath)
                    progress = ProgressBar(saveFilePath, total=content_size, unit="KB", chunk_size=chunk_size, run_status="正在下载",fin_status="下载完成")
                    with open(saveFilePath, "wb") as file:
                        for data in response.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            progress.refresh(count=len(data))
            return True, saveFilePath
        except BaseException as e:
            self.LogE("Down error ==>>  " + str(e))
            return False, saveFilePath

#下载进度
class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (
            self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
            self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)

if __name__ == "__main__":
    VideoDownloadService = VideoDownloadServiceClass()
    videoUrl = "http://v3-dy-y.bytecdn.cn/8049399863f5611a52a58c972ecb8f72/5d0f208b/video/m/220c5c31d4d72d9426fb1f822015dfdc13811625bf7f000067d0dc44f3d8/?rc=MzRpOjY2NTh3bTMzZ2kzQ8ODkzOTUzNDk6NjY5PDNAKXUpQGczdSlAZjN2KUBmaHV5cTFmc2hoZGY7NEBmaWNeL3MyaHBfLS0wLS9zczVvI28jNi8uNS4tLi0tLzEuLy0uL2k6Yi5wIzphLXEjOmAwbyNwYmZyaF4ranQ6Iy8uXg%3D%3D"
    VideoDownloadService.Down(videoUrl, "Video/测试.mp4")