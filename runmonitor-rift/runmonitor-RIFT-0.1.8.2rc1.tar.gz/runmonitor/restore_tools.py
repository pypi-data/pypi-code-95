#!/usr/bin/env python

import os
from runmonitor import environ_check
from runmonitor import check_tools as chu
import ast
from subprocess import Popen,PIPE

def find_env(rmdir,verbose=False,debug=False):
    """
Inputs:
-------
rmdir = the standard runmon directory for the analysis (e.g. RUNMON_BASE/event/cluster:file_path_name/)

Outputs:
--------
returns the path to the environment source if available, else returns None
    """
    if "envinfo.txt" in os.listdir(rmdir):
        if verbose:
            print("found environment info for runmon "+rmdir)
        with open(os.path.join(rmdir,"envinfo.txt")) as f:
            line = f.readline()
        return ast.literal_eval(line)
    else:
        return None 

def analyze(rmdir):
    rundir = chu.read_wocc(rmdir)

def resubmit(rmdir=None,rundir=None,force_pass=False,verbose=False,debug=False,env=None):
    """
Inputs:
-------- 
rmdir = the standard runmon directory
(a correct environment for submission)
fp = force pass; if True, will run force_pass in the directory first

Outputs:
---------
submits the dag
    """

    if rundir == None and rmdir != None:
        rundir = chu.read_wocc(rmdir)
    elif rundir == None:
        raise Exception("no rundir or runmon directory specified, cannnot proceed")
    #if force_pass:
    #    from runmonitor import dagpass as fp
    #    fp.force(wd=rundir,verbose=verbose,debug=debug)
    if env == None:
        os.system("condor_submit_dag "+rundir+"/marginalize_intrinsic_parameters_BasicIterationWorkflow.dag")
    else:
        p = Popen([f"condor_submit_dag {rundir}/marginalize_intrinsic_parameters_BasicIterationWorkflow.dag"],shell=True,stdout=PIPE,
            stderr=PIPE,env=env)
        p.communicate()
 
def get_args(f):
        cip = open(f)
        lines = cip.readlines()
        cip.close()

        args = lines[2].split()
        return args

def get_overflow_index(f):
        args = get_args(f)
        index = -1
        for num in range(len(args)):
                if (args[num] == "--lnL-shift-prevent-overflow"):
                        index = num + 1
                        break
        return index

def get_args_without_overflow(f):
	args = get_args(f)
	new_args = ""
	index = get_overflow_index(f) - 1
	for i in range(len(args)):
		if (i != index and i != index + 1):
			new_args = new_args + args[i] + " "
	new_args = new_args.strip().strip('\"').strip()
	print("!" + new_args)

def search_low_ile_points(itn,rd,thres=0.25):
    """
Inputs:
------------
itn = iteration number (per ILE definition, so index from 0
rd = run directory
thres = what fraction of ILE points need to succeed for this to be successful, defaults 1/4
Outputs:
---------------
returns True/False for above threshold/below threshold respectively
    """
    with open(os.path.join(rd,"marginalize_intrinsic_parameters_BasicIterationWorkflow.dag"),'r') as f:
        lines = f.readlines()
    init = -1
    for i,line in enumerate(lines):
        if 'macroiteration="'+str(itn)+'"' in line:
            init = i
        if init != -1 and "join.sub" in line:
            end = i 
            break 
    ilengoal = (end-init)/2
    ileouts = [el for el in os.listdir(os.path.join(rd,"iteration_"+str(itn)+"_ile")) if "dat" in el]
    ilentrue = len(ileouts)
    if ilentrue <= thres*ilengoal:
        return False
    else:
        return True
       
    
