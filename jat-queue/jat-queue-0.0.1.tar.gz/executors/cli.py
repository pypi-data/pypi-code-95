from re import S
import fire
import json
from .base import ExecutionBackendBase
from multiprocessing import Process
from config import TMConfig
from tasks import Task
from inspect import getmembers, isfunction
import docker
import os

import tasks.tasks as tasks
class ExecutorCLI(ExecutionBackendBase):
    try:
        dclient = docker.from_env()
    except:
        pass
    def __execute__(self, execution_id):
        execution_details = self.get_execution_details(execution_id=execution_id)
        if execution_details:
            self.execution_details = json.loads(execution_details.decode('utf-8'))
            self.log.debug(f"Found execution details to be {self.execution_details}")
            ti = Task(
                    None, 
                    signature=self.execution_details.get('signature'),
                    execution_id=execution_id
            )
            print(self.execution_details)
            ti_process = Process(target=ti, args=self.execution_details.get('args'), kwargs=self.execution_details.get('kwargs', {}))
            ti_process.start()
            ti_process.join()
            return
    
    def execute(self, execution_id: str):
        self.__execute__(execution_id)
        return
    
    def list(self, ):
        functions_list = [o for o in getmembers(tasks)if isfunction(o[1])]
        print(functions_list)
    
    def update_registry(self):
        functions_list = [o for o in getmembers(tasks)if isfunction(o[1])]
        for fname, func in functions_list:
            ti = Task(func)
            print(f"Registering task with signature {ti.signature}")
        
    def build_image(self):
        print(os.path.dirname(os.path.abspath(__file__)))
        self.dclient.images.build(
            path=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            tag=TMConfig.image_tag,
        )
    
fire.Fire(ExecutorCLI)