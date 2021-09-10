#!/usr/bin/env python

#This takes in a run and event (along with the base and cluster environment variables that you have to pass in) and added the appropriate information to archived_runs_microstatus.txt. May be good to call when creating a new run.
import os
import argparse
from runmonitor import environ_check

def update(run,event,base,cluster):
    path = os.path.join(base,event,cluster+":"+run)
    where_on_current_cluster_file = open(path + "/where_on_current_cluster.txt")
    where_on_current_cluster = where_on_current_cluster_file.read().strip()
    where_on_current_cluster_file.close()

    job_status_file = open(path + "/job_status.txt")
    job_status = job_status_file.readlines()[-1].split("\t")[-1].strip()
    job_status_file.close()

    if (job_status == "100000"):
        job_status = "Running"
    elif (job_status == "200000"):
        job_status = "*.dag.dagman.out_Unreadable"
    elif (job_status == "0"):
        job_status = "Finished"
    elif (job_status == "1"):
        job_status = "Failed"
    elif (job_status == "2"):
        job_status = "Aborted"
    else:
        job_status = "Failed_with_error_code_" + job_status

    try:
        with open(base+"/archived_runs_microstatus.txt",'r') as archive:
            archive.seek(0)
            lines=archive.readlines()    
    except:
        lines = []

    with open(base+"/archived_runs_microstatus.txt", "w") as archive:
        exists = False
        if lines == []:
            lines = ["Run:\tEvent:\tPath:\tStatus:\n"]
        for i,line in enumerate(lines):
            if run in line:
                lines[i] = run + "\t" + event + "\t" + where_on_current_cluster + "\t" + job_status+"\n" 
                exists = True
                break
        if exists == False:
            lines += [run + "\t" + event + "\t" + where_on_current_cluster + "\t" + job_status+"\n"]
        archive.writelines(lines)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run", required = True, help = "The run you want to add")
    parser.add_argument("-e", "--event", required = True, help = "The event the run is on")
    parser.add_argument("-b", "--base", required = True, help = "Runmon base")
    parser.add_argument("-c", "--cluster", required = True, help = "Runmon cluster")
    args = parser.parse_args()
    
    update(args.run,args.event,args.base,args.cluster)

