import threading

class RepeatedTimer(threading.Thread):
    def __init__(self, method, delay):
        super().__init__()
        self.daemon = True
        self._stop = threading.Event()
        self.delay = delay
        self.method = method

    def run(self):
        while not self._stop.wait(self.delay):
            self.method()
            
    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()