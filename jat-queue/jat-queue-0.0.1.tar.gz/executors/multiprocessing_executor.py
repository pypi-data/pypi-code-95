from executors.base import ExecutionBackendBase
from multiprocessing import Process

class MPExecutor(ExecutionBackendBase):
    executor_backend = "MultiprocessingExecutor"
    def __execute__(self):
        ti_process = Process(target=self.ti, args=self.execution_details.get('args'), kwargs=self.execution_details.get('kwargs'))
        ti_process.start()
        return 