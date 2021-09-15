
"""
21.08, nash
    시간 체크용 클래스 작성
"""

from time import (
    process_time,
    perf_counter,
    sleep,
)


class Timer:
    """perf_counter timer
    21.08, nash
    """

    def __init__(self):
        self.pc1 = 0
        self.pc2 = 0
        pass

    def check(self):
        self.pc1 = self.pc2
        self.pc2 = perf_counter()
        print(f'time delta: {self.pc2 - self.pc1:.6f} s')

    def diff(self):
        self.pc1 = self.pc2
        self.pc2 = perf_counter()
        return self.pc2 - self.pc1


def main():
    t1 = Timer()
    print('perf_counter started.')
    t1.check()
    for i in range(10):
        t1.check()
        pass


if __name__ == '__main__':
    main()

