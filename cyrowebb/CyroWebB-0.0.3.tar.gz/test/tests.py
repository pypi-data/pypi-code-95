import threading
import time
threads = []

class Thread(threading.Thread):
    def __init__(self,i):
        threading.Thread.__init__(self)
        self.i = i

    def run(self):
        print(f"Thread No. {str(self.i)}")
        time.sleep(5)
        print(f"Thread No. {str(self.i)}")
        time.sleep(5)

for i in range(0,8):
    thread = Thread(i)
    thread.start()