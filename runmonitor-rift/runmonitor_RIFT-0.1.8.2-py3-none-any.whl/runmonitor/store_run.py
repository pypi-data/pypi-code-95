#!/usr/bin/env python
import os
import shutil
from runmonitor import check_environ

def create_envinfo():
    binpath = os.path.join(*sys.executable.split("/")[:-1])
    activatepath = os.path.join(binpath,"activate")
    accounting = os.environ["LIGO_ACCOUNTING"]
    username = os.environ["LIGO_USER_NAME"]
    laldatapath = os.environ["LAL_DATA_PATH"]
    if laldatapath=="":
        laldatapath="''"
    gwsurrogate = os.environ["GW_SURROGATE"]
    if gwsurrogate=="":
        gwsurrogate="''"
    with open("envinfo.sh",'w') as f:
        f.write("source "+activatepath+"\n")
        f.write("export LIGO_ACCOUNTING="+accounting+"\n")
        f.write("export LIGO_USER_NAME="+username+"\n")
        f.write("export LAL_DATA_PATH="+laldatapath+"\n")
        f.write("export GWSURROGATE="+gwsurrogate+"\n")

def store(event,rundir,level=1,rmbase=None,cluster=None,envsh=None):
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
        if envsh != None:
            shutil.copy(envsh,os.path.join(rmdir,"envinfo.sh"))
        else:
            create_envinfo() 

    except Exception as fail:
        print("unable to initialize runmon directory:")
        print(fail)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--level",type=int,default=1,help="The level to get the name from. Defaults to 1 i.e. the rundir, 2 would be the dir the rundir is in, etc.")
    #if necessary, add more logic so that you specify if non-primary where to get the name from. Currently assumes not primary --> secondary i.e. ../descriptive_name/rundir/*
    parser.add_argument("--rundir",type=str,help="the run directory")
    parser.add_argument("--event",type=str,help="the string representing the event being run on")
    parser.add_argument("--rmbase",type=str,default=None,help="the base runmon directory. If RUNMON_BASE is already in the env variables (and you want to use this as your base), do not pass this")
    parser.add_argument("--cluster",type=str,default=None,help="the cluster this is maintained on. This should be fixed, so you should probably just set the RUNMON_CLUSTER env, but this is an alternative if necessary")
    parser.add_argument("--envsh",type=str,default=None,help="a path to a single script that sets up the environment, to allow for self healing")
    opts = parser.parse_args()
   
    store(opts.event,opts.rundir,level=opts.level,rmbase=opts.rmbase,cluster=opts.cluster,envsh=opts.envsh)
