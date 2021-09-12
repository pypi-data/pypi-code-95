# from executors import start_worker_pool
# from gevent import monkey; monkey.patch_all()
import fire
from . import start_worker_pool


class ExtendedPackageCLI():
    def worker(self, ):
        start_worker_pool()

def package_cli():
    fire.Fire(ExtendedPackageCLI)