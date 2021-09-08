#!/usr/bin/env python

import os
from runmonitor import environ_check
from runmonitor import check_up as chu

def find_env(rmdir,verbose=False,debug=False):
    """
Inputs:
-------
rmdir = the standard runmon directory for the analysis (e.g. RUNMON_BASE/event/cluster:file_path_name/)

Outputs:
--------
returns the path to the environment source if available, else returns None
    """
    if "envinfo.sh" in os.listdir(rmdir):
        if verbose:
            print("found environment info for runmon "+rmdir)
        return os.path.join(rmdir,"envinfo.sh")
    else:
        return None 

def analyze(rmdir):
    


    rundir = chu.read_wocc(rmdir)

def resubmit(rmdir,fp=False,verbose=False,debug=False):
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
    rundir = chu.read_wocc(rmdir)
    os.chdir(rundir)
    if fp:
        import force_pass as fp
        fp.force(wd=rundir,verbose=verbose,debug=debug
    os.system("condor_submit_dag marginalize_intrinsic_parameters_BasicIterationWorkflow.dag")   
 




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",action='store_true')
    parser.add_argument("--debug",action='store_true')
    parser.add_argument("--rmdir",type=str,help="the run monitoring directory for the analysis")
    opts = parser.parse_args()
    
    if opts.debug:
        print(find_env(opts.rmdir,verbose=opts.verbose,debug=opts.debug))
    resubmit(opts.rmdir,debug=opts.debug,verbose=opts.verbose)
