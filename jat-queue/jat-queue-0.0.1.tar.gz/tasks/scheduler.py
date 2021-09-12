from datetime import time
import json
from tasks import Task
from time import sleep
import logging


class ExecutionBase(Task):
    queue_id = "alcatraz"
    execution_args = []
    execution_kwargs = {}
    log = logging.getLogger(__name__)

    def __getstate__(self,):
        if self.finished:
            return {
                'task_id':  self.task_id,
                'started_at' : self.started_at,
                'finished_at': self.finished_at,
                'duration': self.finished_at - self.started_at,
                'state': self.task_state,
                'hostname': self.hostname,
                'log': self.task_io.getvalue(),
                'return_val': self.return_val,
                'task_signature': self.signature
            }
        return {
            'task_id':  self.task_id,
            'started_at' : self.started_at,
            'state': self.task_state,
            'hostname': self.hostname,
            'log': self.task_io.getvalue(),
        }
    
    def __save_state(self, ):
        state_dict = json.dumps(self.__getstate__(), default=str)
        self.redis.set(f'{self.task_id}_meta', state_dict)
    
    def save_task_state(self, ):
        self.__save_state()

    def start(self, ):
        return
    
    def get_registered_tasks(self, ):
        rts = self.redis.lrange('registered_tasks', 0, -1)
        if rts:
            return list(map(lambda x: x.decode('utf-8'), rts))
        
        return []
    
    def _queue_task(self, *args, **kwargs):
        self.execution_id = f"execution_{self.gen(n=10)}"
        execution_state = json.dumps(self.get_execution_state(), default=str)
        self.redis.publish(self.queue_id, self.execution_id)
        self.redis.set(self.execution_id, execution_state)
        self.log.debug(f"Sent out a message to queue this task, execution_id was {self.execution_id}")
        self.redis.rpush(f"task_queue-{self.queue_id}", self.execution_id)

    def get_execution_state(self, ):
        return {
            'execution_id': self.execution_id,
            'task_id':  self.task_id,
            'args': self.execution_args,
            'kwargs': self.execution_kwargs,
            'started_at' : self.started_at,
            'state': self.task_state,
            'hostname': self.hostname,
            'signature': self.signature,
            'log': self.task_io.getvalue(),
        }
    
    


class Scheduler(ExecutionBase):
    execution_status = "Queued"
    def __init__(self, signature) -> None:
        super().__init__(None, signature=signature)
        registered_tasks = self.get_registered_tasks()
        if not signature or  signature not in registered_tasks:
            raise ValueError("Unable to execute the task, invalid signature provided")
        
    def queue(self, *args, **kwargs):
        self.execution_args = args
        self.execution_kwargs = kwargs
        self._queue_task(*args, **kwargs)