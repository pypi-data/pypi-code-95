from executors.base import ExecutionBackendBase

class LocalExecutor(ExecutionBackendBase):
    executor_backend = "LocalExecutor"
    def __execute__(self):
        self.ti(
            *self.execution_details.get('args'), 
            **self.execution_details.get('kwargs')
        )
        return super().__execute__()