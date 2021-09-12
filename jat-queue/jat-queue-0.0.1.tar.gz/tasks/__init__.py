import abc
import logging
import os
import secrets
import datetime
import string
import pickle
import socket
import marshal, types
from typing import Any
import redis
from config import TMConfig
from hashlib import md5
from contextlib import redirect_stdout
import io
import time
import json
logging.basicConfig()
log = logging.getLogger(__name__)
# initializing size of string 
N = 7
  
# using random.choices()
# generating random strings 

class TaskUtils():
    log = logging.getLogger(__name__)
    log.setLevel("DEBUG")
    @staticmethod
    def gen(n=5):
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                                                  for i in range(n))

class TaskStateHandler(TaskUtils):
    full_log = ""
    def __getstate__(self,):
        if self.finished:
            return {
                'task_id':  self.task_id,
                'started_at' : self.started_at,
                'finished_at': self.finished_at,
                'duration': self.finished_at - self.started_at,
                'state': self.task_state,
                'hostname': self.hostname,
                'log': self.full_log,
                'return_val': self.return_val,
                'task_signature': self.signature
            }
        return {
            'task_id':  self.task_id,
            'started_at' : self.started_at,
            'state': self.task_state,
            'hostname': self.hostname,
            'log': self.full_log,
        }
    
    def __save_state(self, ):
        state_dict = self.__getstate__()
        current_dict  = self.redis.get(self.execution_id)
        if current_dict:
            current_dict = json.loads(
                current_dict.decode('utf-8')
            )
            state_dict = {**current_dict, **state_dict}
        
        state_dict = json.dumps(state_dict, default=str)
        if self.execution_id:
            self.redis.set(f'{self.execution_id}', state_dict)
                
        self.redis.set(f'{self.task_id}_meta', state_dict)
    
    def save_task_state(self, ):
        self.__save_state()

class TaskPickler(TaskStateHandler):
    def pickle_task(self,):
        if os.path.exists(f'{self.signature}.pkl'):
            log.debug(f"Task signature pickle already present {self.signature}")
            return
        with(open(f'{self.signature}.pkl', 'wb') as pkl_task):
            
            marshal.dump(self.exec_function.__code__, pkl_task)
    
    def pickle_load(self, ):
        with(open(f'{self.signature}.pkl', 'rb') as pkl_task):
            code = marshal.load(pkl_task)
            self.exec_function = types.FunctionType(code, globals(), self.signature)
    
    def register_task(self,):        
        # task_signature = md5(self.exec_function.__code__)[:10]
        self.pickle_task()
        tasks = list(map(lambda x:x.decode('utf-8'), self.redis.lrange('registered_tasks', 0, -1)))
        if tasks and self.signature in tasks:
            log.debug(f"Task with signature {self.signature} already present")
            return
        self.redis.rpush("registered_tasks", self.signature)


class Task(abc.ABC, TaskPickler):
    task_state = "Initialized"
    task_io = io.StringIO()
    redis = redis.from_url(TMConfig.redis_url)
    finished = False
    signature = None
    execution_id = None
    return_val = ""
    @staticmethod
    def hostname():
        return socket.gethostname()
    
    def __init__(self, function, signature=None, execution_id=None) -> None:
        super().__init__()
        if execution_id:
            self.execution_id = execution_id
        if signature :
            self.signature = signature
            self.pickle_load()
        elif function:
            self.exec_function = function
            self.signature = function.__name__
            self.register_task()

        self.initiate_task_meta()
    
    def initiate_task_meta(self):
        if self.execution_id:
            self.task_id = self.execution_id
        else:
            self.task_id = self.gen()
        log.debug(f"Function signature is {self.exec_function.__name__}")
        self.started_at = datetime.datetime.utcnow()
        self.hostname = self.hostname()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.task_state = "Running"
        self.save_task_state()
        task_io = io.StringIO()
        log.debug(f"Starting execution for execution_id {self.execution_id}")
        try:
            with redirect_stdout(task_io):
                self.return_val =  self.exec_function(*args, **kwds)
            self.full_log = task_io.getvalue()
            self.task_state = "Success"
            self.finished_at = datetime.datetime.utcnow()
        except Exception as e:
            self.task_state = "Failure"
            self.finished_at = datetime.datetime.utcnow()
        finally:
            self.task_io = task_io
            self.finished = True
            self.save_task_state()  
            log.debug(
                f"""Execution finished for execution_id {self.execution_id}, took {self.finished_at - self.started_at}s to finish"""
            )


class Executor(Task):
    def __init__(self, signature) -> None:
        super(Task).__init__()
        registered_tasks = self.redis.get('registered_tasks')
        if not signature or not(registered_tasks) or signature not in registered_tasks:
            raise ValueError("Unable to execute the task, invalid signature provided")
        
        super().__init__(function=None, signature=signature)

    def execute(self, *args, **kwargs):
        self.__call__(*args, **kwargs)
    



if __name__ == "__main__":
    add(1,2)