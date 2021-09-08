#!/usr/bin/env python

from runmonitor import environ_check

import os
import argparse
from runmonitor import stat_rd as srd
import time
#import classad
#import htcondor
#import python-daemons

#functions to call for autmoatic update of public facing runmon directory, using stat_rd.py tools

def read_wocc(pd,debug=False,verbose=False):
    """
A simple helper function now defined separately so that it can be called in other scripts

Inputs:
--------
pd = public directory (RUNMON_BASE/event/cluster:run_path_name/

Outputs:
---------
returns the run directory
    """
    try:
        wocc = os.path.join(pd,"where_on_current_cluster.txt")
        if verbose:
            print(wocc)
        with open(wocc,'r') as f:
            rd = f.readline().strip()
        return rd
    except Exception as failure:
        if debug:
            print(failure)
        print("Unable to read run directory from where_on_current_cluster.txt, please verify that it exists and is accessible")
        return None

def update(pd,rd=None,debug=False,verbose=False):
    """
Inputs:
pd = public directory where the analysis is taking place. Depending how this function is being used, may be constructed algorithmically from run data + RUNMON_BBASE environment variable
rd = run directory, if public directory is configured with where_on_current_cluster.txt then this will be handled automatically
debug = produce error messages etc. for debugging
verbose = print human readable statements

-----------
Outputs:
Updates to files convergence.txt, extrinsic_exists.txt, job_status.txt,dag_id.txt
returns ???

    """
    #first, logic to read rd from wocc if available, and write wocc if rd is explicitly given
    if rd==None:
        rd = read_wocc(pd)
    else:
        wocc = os.path.join(pd,"where_on_current_cluster.txt")
        with open(wocc,'w') as f:
            f.write(rd)
    #use scan_samples to obtain information from the run directory
    sampdat = srd.scan_samples(rd,debug=debug,verbose=verbose)
    #go about writing that information to respective files
    #also, a gmt timestamp 
    asctime = time.asctime(time.gmtime(time.time()))
    if sampdat[2] != 0:
        itn = "e"
        expath = os.path.join(pd,"extrinsic_exists.txt")
        with open(expath,'w') as f:
            f.write(str(sampdat[2]))
    else:
        if debug:
            print(sampdat[0].split("/")[-1])
            print(sampdat[0].split("/")[-1].strip())
            print(sampdat[0].split("/")[-1].strip().split(".")[0])
            print(sampdat[0].split("/")[-1].strip().split(".")[0].split("-")[1])
        itn = sampdat[0].split("/")[-1].strip().split(".")[0].split("-")[1]
    conpath = os.path.join(pd,"convergence.txt")
    with open(conpath,'a') as f:
        f.write(asctime+"\t"+itn+"\t"+str(sampdat[3])+"\t"+str(sampdat[1])+"\n")
    #using query_dag_exit to get job status
    jstpath = os.path.join(pd,"job_status.txt")
    statint = srd.query_dag_exit(rd,debug=debug,verbose=verbose)
    with open(jstpath,'a') as f:
        f.write(asctime+"\t"+str(statint)+"\n")
    #using query_dag_id to get current dag id
    dagidpath = os.path.join(pd,"dag_id.txt")
    dagid = srd.query_dag_id(rd,debug=debug,verbose=verbose)
    with open(dagidpath,'w') as f:
        f.write(str(dagid))
    if debug:
        return pd,rd
    else:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pd",type=str,help="the public directory to write into")
    parser.add_argument("--rd",type=str,default=None,help="the run directory, if the public directory is configured already then it can be found in where_on_current_cluster.txt, so need not be passed")
    parser.add_argument("--verbose",action="store_true",help="for verbose output")
    parser.add_argument("--debug",action="store_true",help="for debugging output")
    opts = parser.parse_args()

    print(update(opts.pd,rd=opts.rd,verbose=opts.verbose,debug=opts.debug))
