import pandas as pd
import yaml

from dwhutils.db_connection import connect_to_db
from dwhutils.Docker import Orchestrierung
from time import sleep
from sqlalchemy import create_engine

class Job:
    def __init__(self, jobname: str, jobid: str, triggername: str, triggerid: int, processingdate: str,
                 containername: str, CreateContainerFirst: bool = False):
        self.jobname = jobname
        self.jobid = jobid
        self.triggername = triggername
        self.triggerid = triggerid
        self.processingdate = processingdate
        self.containername = containername
        self.CreateContainerFirst = CreateContainerFirst


    def start(self):
        test = True

        while test:
            if self.checkTrigger():
                self.run()
                test = False
            else:
                print("wait for trigger")

            sleep(1)



    def run(self):
        print("start job")
        Orchester = Orchestrierung(containerName=self.containername, MustCreate=False, imageName='source_python', cpuInCores=1,
                                   memoryInGB=1, tag="v1")
        Orchester.startContainer()
        Orchester.runCommandInContainer("python3 main_source.py {p}".format(p=self.processingdate))
        print("end job")
        insert = "INSERT INTO tech.trigger(triggername, trigger_id, job_id, job_name, activitytime," \
                 " processingdate, activitydate)VALUES('bizENB', 20, '2', 'bizENB', NOW(), '{p}', NOW());".format(p=self.processingdate)
        con = connect_to_db()
        con.execute(insert)
        Orchester.stopContainer()





    def checkTrigger(self):
        trigger_table = pd.read_sql_table(table_name="trigger", schema="tech", con=connect_to_db())
        last_run = trigger_table[trigger_table["job_id"] == self.jobid]
        if last_run.shape[0] > 0:
            return True
        else:
            return False
