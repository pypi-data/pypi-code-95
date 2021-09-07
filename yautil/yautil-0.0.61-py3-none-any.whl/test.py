

def double(x: int) -> int:
    return x * 2


if __name__ == '__main__':
    from mputil import MpUtil

    data = [0, 1, 2, 3, 4, 5]

    with MpUtil(total=len(data)) as mp:
        for d in data:
            mp.schedule(double, d)
        results = mp.wait()

    for i, y in enumerate([0, 2, 4, 6, 8, 10]):
        assert y == results[i]