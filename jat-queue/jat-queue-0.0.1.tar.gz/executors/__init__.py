from .local_executor import LocalExecutor
from .docker_executor import DockerExecutor
from .multiprocessing_executor import MPExecutor
from .gevent_executor import GeventExecutor
from config import TMConfig

def get_executor():
    # Supported executors in config.ini 
    # MultiProcessingExecutor - Uses python multiprocessing to spawn tasks
    # LocalExecutor - Use a very simple single threaded task executor which executes task one by one
    # DockerExecutor - Spawn a python container(docker container) and execute the registered task
    # GeventExecutor - Use Gevent to create concurrent tasks
    if TMConfig.executor_backend == "MultiProcessingExecutor":
        return MPExecutor
    elif TMConfig.executor_backend == "LocalExecutor":
        return LocalExecutor
    elif TMConfig.executor_backend == "DockerExecutor":
        return DockerExecutor
    elif TMConfig.executor_backend == "GeventExecutor":
        return GeventExecutor

def start_worker_pool():
    executor_instance = get_executor()()
    executor_instance.start()
