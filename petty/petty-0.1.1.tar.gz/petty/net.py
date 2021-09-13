import os.path
import urllib

import urllib3


def download_with_urllib3(url: str,  download_dir: str, filename: str, times: int = 10):
    if download_dir is None:
        download_dir = '.'
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    if not filename:
        filename = os.path.basename(url)

    filepath = os.path.join(download_dir, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10:
        return

    CHUNK = 16 * 1024
    http = urllib3.PoolManager()

    try:
        r = http.request('GET', url, retries=times, preload_content=False)
        if r.status != 200:
            return
        with open(filepath, 'wb') as f:
            for chunk in r.stream(CHUNK):
                f.write(chunk)
    except urllib3.exceptions.NewConnectionError:
        print("Cound not connect to", url)
    finally:
        r.release_conn()


def read_with_urllib3(url: str, times: int = 10):
    """访问一个url，并返回内容

    Args:
        url (str): 链接
        times (int, optional): 重试次数. Defaults to 10.
    """
    http = urllib3.PoolManager()
    try:
        r = http.request('GET', url, retries=times)
        if r.status != 200:
            return
        return r.data
    except urllib3.exceptions.NewConnectionError:
        print("Cound not connect to", url)
    finally:
        r.release_conn()


def download(url: str,  download_dir: str, filename: str, retries: int = 10):
    """下载，使用urlopen下载。

    Args:
        url (str): 下载URL
        download_dir (str): 下载目录
        filename (str): 保存的文件名
        retries (int, optional): 重试的最大次数. Defaults to 10.
    """
    if download_dir is None:
        download_dir = '.'
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    if not filename:
        filename = os.path.basename(url)

    filepath = os.path.join(download_dir, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10:
        return

    times = 0
    flag = True
    CHUNK = 16 * 1024
    while flag:
        if times > retries:
            print(url, "Download Failed!")
            break
        try:
            with urllib.request.urlopen(url) as response:
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = response.read(CHUNK)
                        if not chunk:
                            break
                        f.write(chunk)
        except Exception as e:
            if 'HTTP Error 404' in str(e):
                return
            if '<urlopen error [WinError' in str(e):
                pass
            times += 1

        if os.path.getsize(filepath) > 10:
            break
        print(url, '下载失败，重试{}'.format(times))


def read(url: str, retries: int = 10):
    """访问一个url，并返回内容（urlopen）

    Args:
        url (str): 链接
        retries (int, optional): 重试次数. Defaults to 10.
    """
    times = 0
    flag = True
    while flag:
        if times > retries:
            break
        try:
            with urllib.request.urlopen(url) as f:
                data = f.read()
                if len(data) > 10:
                    return data
                times += 1
        except Exception as e:
            if 'HTTP Error 404' in str(e):
                return
            if '<urlopen error [WinError' in str(e):
                pass
            times += 1
