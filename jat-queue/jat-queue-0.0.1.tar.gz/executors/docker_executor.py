from os import name
from executors.base import ExecutionBackendBase
import docker
from config import TMConfig

class DockerExecutor(ExecutionBackendBase):
    executor_backend = "DockerExecutor"
    try:
        dclient = docker.from_env()
    except:
        pass
    def __execute__(self):
        container = self.dclient.containers.run(
            image=TMConfig.image_tag,
            command=["/bin/bash", "-c", f"cd /task_queue && python -m executors.cli execute --execution_id {self.execution_id}"],
            detach=True,
            name=self.execution_id,
            # auto_remove=True,
        )
        # self.dclient.containers.run('alpine', 'echo hello world')
        print("Ooooo")
        # self.ti(
        #     *self.execution_details.get('args'), 
        #     **self.execution_details.get('kwargs')
        # )
        return super().__execute__()