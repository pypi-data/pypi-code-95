from executors.base import ExecutionBackendBase
import gevent
# from gevent import monkey

# monkey.patch_all()
class GeventExecutor(ExecutionBackendBase):
    executor_backend = "GeventExecutor"
    queue = []
    def __execute__(self):
        thread = gevent.spawn(
            self.ti, 
            *self.execution_details.get('args'),
            **self.execution_details.get('kwargs')
        )
        gevent.sleep(0)
        thread.start()
        # thread.join()
        # self.queue.append(thread)
        # if len(self.queue) >=5:
        #     gevent.joinall(self.queue)
        #     self.queue = []


        # ti_process = Process(target=self.ti, args=self.execution_details.get('args'), kwargs=self.execution_details.get('kwargs'))
        # ti_process.start()
        return 