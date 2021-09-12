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
logging.basicConfig()

import socket

class ExecutionBackendBase(abc.ABC):
    daemon_sleep_interval = 10
    redis = redis.from_url(TMConfig.redis_url)
    queue_id = TMConfig.redis_channel
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
        
        for message in subscription.listen():
        # while True:
        #     message = subscription.get_message()
            if message :
                self.log.debug(message)
                data = message.get('data', "")
                if type(data) in [bytes, str]:
                    execution_id = str(data, "utf-8")
                    self.execution_id = execution_id
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
            else:
                # sleep(self.daemon_sleep_interval)
                self.log.debug(f"Came out of a {self.daemon_sleep_interval}s sleep")
            
        return