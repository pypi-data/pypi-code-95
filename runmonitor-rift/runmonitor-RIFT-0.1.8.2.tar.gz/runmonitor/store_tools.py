#!/usr/bin/env python
import os
import shutil
import sys
from runmonitor import environ_check

def create_envinfo(rundir):
    envdat = os.environ.copy()
    with open(os.path.join(rundir,"envinfo.txt"),'w') as f:
        f.write(str(envdat))

def store(event,rundir,level=1,rmbase=None,cluster=None,envdat=None):
    if rmbase == None:
        rmbase = os.environ['RUNMON_BASE']
    if cluster == None:
        cluster = os.environ['RUNMON_CLUSTER']
    print(rundir.strip("/").split("/"))
    name = rundir.strip("/").split("/")[-1*level]
    if event not in os.listdir(rmbase):
        os.mkdir(os.path.join(rmbase,event))
    rmdir = os.path.join(rmbase,event,cluster+":"+name)
    try:
        os.mkdir(rmdir)
        with open(os.path.join(rmdir,"where_on_current_cluster.txt"),'w') as f:
            f.write(rundir)
        if envdat == "generate":
            create_envinfo(rundir)
            shutil.copy(os.path.join(rundir,"envinfo.txt"),os.path.join(rmdir,"envinfo.txt"))
        elif envdat != None:
            shutil.copy(envdat,os.path.join(rmdir,"envinfo.txt"))

    except Exception as fail:
        print("unable to initialize runmon directory:")
        print(fail)

