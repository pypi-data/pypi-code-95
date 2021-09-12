from typing import Type

def netrandom2(checker: Type[Checker], limit=1000000, workers=512):
    """Make netrandom checks with check_fn,
    filtering results with filter_fn,
    then process results by result_fn"""
    import sys
    if type(checker) is Checker:
        raise ValueError('Checker must be Checker type (not an instance).')

    threads = []

    checker.set_generator(random_wan_ips(limit))

    results = []

    for _ in range(workers):
        t = checker()
        threads.append(t)

    checker.set_running(True)

    try:
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        checker.set_running(False)
        sys.stderr.write('\rStopping...\n')

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        sys.stderr.write('\rKilled\n')

    return results
