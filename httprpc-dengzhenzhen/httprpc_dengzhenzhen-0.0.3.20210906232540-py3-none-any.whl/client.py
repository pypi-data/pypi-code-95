import requests
import threading
import time

def do_get(n):
    start = time.time()
    res = requests.get('http://127.0.0.1:5000', timeout=n)
    print(time.time() - start)
    return res.content

if __name__ == '__main__':
    for i in range(1, 1000):
        try:
            print(i)
            threading.Thread(target=do_get, args=(None,)).start()
        except Exception as e:
            print(e.with_traceback(None))
