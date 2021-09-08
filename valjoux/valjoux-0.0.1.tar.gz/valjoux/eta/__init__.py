from datetime import datetime
from time import perf_counter


class Eta:
    def __init__(self, log=False):
        self.curr = 0
        self.log = log

    def lap_milli(self):
        prev = self.curr
        self.curr = perf_counter()
        return self.curr - prev

    def ini(self, message=''):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.curr = perf_counter()
        output = f"[ini] {timestamp} {message}"
        return print(output) if self.log else output

    def lap(self, message=''):
        lap_milli = self.lap_milli()
        output = f"[lap] +{lap_milli :0.6f}s {message}"
        return print(output) if self.log else output

    def end(self, message=''):
        prev = self.curr
        self.curr = perf_counter()
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # %Y-%m-%d
        output = f"[end] {timestamp} (+{(self.curr - prev):0.6f}s) {message}"
        return print(output) if self.log else output
