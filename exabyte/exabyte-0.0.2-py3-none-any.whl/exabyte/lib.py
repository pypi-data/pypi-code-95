def init_worker(key):
    import os
    from string import Template
    cmd = 'dask-worker {} > /dev/null 2>&1'.format(key)
    os.system(cmd)


def start(key):
    import joblib
    from dask.distributed import Client
    client = Client(host=key,threads_per_worker=2,processes=False,dashboard_address=8787)
    init_worker(key);


def run(function):
    with joblib.parallel_backend(‘dask’):
        function()
