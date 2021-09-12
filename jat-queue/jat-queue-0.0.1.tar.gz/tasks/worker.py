from datetime import datetime
import types
import redis
import abc
from tasks import Task
from time import sleep
from config import TMConfig
import redis
import json
import logging
import io
from multiprocessing import Process
from contextlib import redirect_stdout
logging.basicConfig()

import socket

class WorkerBase(abc.ABC):
    daemon_sleep_interval = 10
    redis = redis.from_url(TMConfig.redis_url)
    queue_id = "alcatraz"
    executor_backend = None
    log = logging.getLogger(__name__)
    log.setLevel("DEBUG")
    task_state = "Initialized"
    task_io = io.StringIO()
    
    def get_execution_details(self, execution_id):
        return self.redis.get(execution_id)
    
    def print_start_worker_meta(self):
        meta_string  = f"""
            Worker starting at host {socket.gethostname()} at {datetime.utcnow()}
            Rotation period for our worker is {self.daemon_sleep_interval}
            Worker execution backend is {self.executor_backend}
            Queue bound to - {self.queue_id}
            Redis backend at - {TMConfig.redis_url}

        """
        # self.log.info(f"Worker starting at host {socket.gethostname()}\n\nStarted worked at time {datetime.utcnow()}\n\nOur worker has a standard daemon time of {self.daemon_sleep_interval} seconds :)")
        self.log.info(meta_string)

    @abc.abstractmethod
    def __execute__(self,):
        pass

    def start(self,):
        subscription = self.redis.pubsub()
        subscription.subscribe(self.queue_id)
        self.print_start_worker_meta()
        
        while True:
            message = subscription.get_message()
            if message :
                self.log.debug(message)
                data = message.get('data', "")
                if type(data) in [bytes, str]:
                    execution_id = str(data, "utf-8")
                else:
                    continue
                # execution_id = execution_id.decode('utf-8')
                self.log.debug(f"Execution ID queued up is {execution_id}")
                execution_details = self.get_execution_details(execution_id)
                if execution_details:
                    self.execution_details = json.loads(execution_details.decode('utf-8'))
                    self.log.debug(f"Found execution details to be {self.execution_details}")
                    self.ti = Task(
                            None, 
                            signature=self.execution_details.get('signature'),
                            execution_id=execution_id
                    )

                    self.__execute__()
                    # ti(
                    #     *execution_details.get('args'), 
                    #     **execution_details.get('kwargs')
                    # )

                    
            
            sleep(self.daemon_sleep_interval)
            self.log.debug(f"Came out of a {self.daemon_sleep_interval}s sleep")
            
        return
    
class LocalWorker(WorkerBase):
    executor_backend = "LocalExecutor"
    def __execute__(self):
        self.ti(
            *self.execution_details.get('args'), 
            **self.execution_details.get('kwargs')
        )
        return super().__execute__()

class MPWorker(WorkerBase):
    executor_backend = "MultiprocessingExecutor"
    # pool = multiprocessing.Pool()
    def __execute__(self):
        # with redirect_stdout(self.task_io):
            # self.return_val =  self.exec_function(*args, **kwds)
        ti_process = Process(target=self.ti, args=self.execution_details.get('args'), kwargs=self.execution_details.get('kwargs'))
        ti_process.start()
        # self.ti(
        #     *self.execution_details.get('args'), 
        #     **self.execution_details.get('kwargs')
        # )
        return super().__execute__()
    
    


# LocalWorker().start()
MPWorker().start()