import time
import sqlq
import threading
import traceback


class base_worker(object):
    terminate = False
    terminated = False
    exploded = False
    exploded_reason = None
    app_root = None
    sql = None
    writer = None
    export_functions = None
    invert_worker = False
    under_maintenance = False
    maintenance_job_done = False

    def job(self) -> None:
        pass

    def worker(self) -> None:
        while not self.terminate:
            try:
                under_maintenance = self.under_maintenance
                if self.invert_worker:
                    under_maintenance = not under_maintenance
                    if under_maintenance:
                        self.maintenance_job_done = False
                if under_maintenance or self.maintenance_job_done:
                    time.sleep(5)
                    continue
                self.job()
                if self.invert_worker and not under_maintenance:
                    self.maintenance_job_done = True
            except:
                self.exploded_reason = traceback.format_exc()
                self.exploded = True
                break
        if self.terminate:
            self.terminated = True

    def stop(self) -> None:
        self.terminate = True
        while not self.terminated:
            time.sleep(1 / 1000)

    def start(self) -> None:
        p = threading.Thread(target=self.worker)
        p.daemon = True
        p.start()


