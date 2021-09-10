#!/usr/bin/env python

# functions to call for run directory status updates.

import os
import argparse
import subprocess
from runmonitor import environ_check
#imports that may be useful for new features in the future:
#import classad
#import htcondor
#import psutil
#import python-daemon

def read_test(rd,it):
    #a helper function for finding and reading the test output associated with a given iteration
    #open last iterations test directory (test indexes like posterior_samples, so no -1 needed
    tlogs = os.listdir(rd+"/iteration_"+str(it)+"_test/logs/")
    try:
        #get the outfile
        outf = [f for f in tlogs if "out" in f][0]
        #read the outfile
        with open(rd+"/iteration_"+str(it)+"_test/logs/"+outf,'r') as f:
            tvalue = float(f.readline().strip())
    except: 
        tvalue = "10000000"
        #sometimes test output may not be printed, in which case we will return this
    return tvalue

def scan_samples(rd,debug=False,verbose=False,js=False):
    #TODO js flag functionality
    """
    inputs:
    -------- 
    run directory, debug flag, verbose flag, js flag

    outputs: 
    --------
    If samples are found, a list with 4 elements:
    [0] : path to most recent samples
    [1] : number of points in all.net
    [2] : number of points in extrinsic if applicable, else 0
    [3] : read value of most recent test output (last iteration if extrinsic), js between most recent and second most recent instead if that flag is applied
    
    If no samples are found returns None    
    """
    rd_contents = os.listdir(rd) 
    #files with both "sample" and "dat" in their name should be posterior_samples files of some variety
    samples = sorted([f for f in rd_contents if 'sample' in f and 'dat' in f])
    #choose posterior_samples that aren't extrinsic then order them by their iteration number
    insamples = sorted([f for f in samples if "extrinsic" not in f],key=lambda f: int(f.split("-")[1].split(".")[0]))
    #presuming we have intrinsic samples, we will want to get these numbers (even if extrinsic is done
    if insamples != []:
        #wc -l to figure out the number of lines in all.net, should be much faster than actually reading the file; technically off by 1, but since number shouldbe O(10k) it's not worth the bother to fix
        ptnall = subprocess.check_output(["wc","-l",rd+"/all.net"],text=True).strip().split()[0]
        #get the last iteration index, then feed it to read_test
        lastit = insamples[-1].split("-")[1].split(".")[0]
        testv = read_test(rd,lastit)
        if debug:
            print(lastit)
    else:
        testv = 10000000
    if debug: #printing all the files being read in case something is going wrong
        print(samples)
    if "extrinsic_posterior_samples.dat" in samples:
        #same as ptnall above
        ptnext = subprocess.check_output(["wc","-l",rd+"/extrinsic_posterior_samples.dat"],text=True).strip().split()[0]
        #prints and returns
        if verbose:
            print("Extrinsic samples available at: "+rd+"/extrinsic_posterior_samples.h5")
            print("all.net contains "+str(ptnall)+" points")
            print("Extrinsic samples contain "+str(ptnext)+" extrinsic points")
            if js:
                print("js not yet implemented") #TODO part of implementing js is changing this    
            else: 
                print("Final intrinsic iteration had test value "+str(testv))
        return [rd+"/extrinsic_posterior_samples.h5",ptnall,ptnext,testv]
        
    elif insamples != []: 
        if verbose:
            print("Intrinsic samples (most recent) available at: "+rd+"/"+insamples[-1])
            print("all.net contains "+str(ptnall)+" points")
            print("Most recent intrinsic iteration had test value "+str(testv))
        return [rd+"/"+insamples[-1],ptnall,0,testv]

    else:
        if verbose:
            print("No samples available")
        return [rd+"/posterior_samples_-1.dat",0,0,testv]

def query_dag_exit(rd,debug=False,verbose=False):
    """
    inputs:
    --------
    run directory to view, debug and verbose flags

    outputs:
    ---------
    If no exit status found, returns 100000. If dag is unreadable returns 200000. If exit status found, returns exit status

    """
    try:
        lastline = subprocess.check_output(["tail","-n 1",rd+"/marginalize_intrinsic_parameters_BasicIterationWorkflow.dag.dagman.out"],text=True).strip()
        if debug:
            print(lastline)
        if "EXITING" not in lastline:
            if verbose:
                print("DAG has not performed a standard exit. This likely means it is still running, but could also indicate a bad exit") 
            return 100000 #returning an integer for consistency. This shouldn't be a possible error code from dag. If it is, I have no idea what they are doing...
        #TODO integrate with htcondor utils to differentiate between these bad exits and still running cases
        # If it has exited with a status, the return will be that status. If it's an easily identifiable status, then verbose will print what it means accordingly
        elif lastline.split()[-1] == "0":
            if verbose:
                print("DAG has exited with success signal")
            return int(lastline.split()[-1])
        elif lastline.split()[-1] == "1":
            if verbose:
                print("DAG has exited with failure signal")
            return int(lastline.split()[-1])
        elif lastline.split()[-1] == "2":
            if verbose:
                print("DAG has exited with SIGUSR signal")
            return int(lastline.split()[-1])
        else:
            if verbose:
                print("DAG has exited with an unknown error")
            return int(lastline.split()[-1])
    except Exception as failure:
        print("DAG reading failed with exception: "+str(failure))
        return 200000 # a recognizable int error code for unreadable .dagman.out
              
def query_dag_id(rd,debug=False,verbose=False):
    """
inputs:
----------
rd = run directory
debug and verbose flags

outputs:
----------
The id of the marginalize...dag (with one trailing 0 after the decimal)

    """
    with open(os.path.join(rd,"marginalize_intrinsic_parameters_BasicIterationWorkflow.dag.dagman.log"),'r') as f:
        lines = f.readlines()[:-1] #stripping the last ... element
    
    if debug:
        print(lines)
    lastlines = []
    for i,line in reversed(list(enumerate(lines))):
        if line == "...\n":
            lastlines = lines[i+1:]
            break
    if debug:
        print(lastlines)
    if lastlines != []:
        dagid = lastlines[0]
    dagid = dagid.split(" ")[1].strip("()").split(".")[0]
    dagid = dagid+".0"
    if debug:
        print(dagid)
    return dagid

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",action='store_true',help="pass for verbose output")
    parser.add_argument("--rd",type=str,help="the run directory being scanned, absolute path")
    parser.add_argument("--debug",action='store_true',help="pass for debug information")
    opts = parser.parse_args()    

    print(scan_samples(opts.rd,debug=opts.debug,verbose=opts.verbose))
    print(query_dag_exit(opts.rd,debug=opts.debug,verbose=opts.verbose))
    print(query_dag_id(opts.rd,debug=opts.debug,verbose=opts.verbose))
