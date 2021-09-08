#!/usr/bin/env python

#A script wrapper for manually calling the store_tools.py function store()

import os
import argparse
from runmonitor import store_tools as sto

parser = argparse.ArgumentParser()
parser.add_argument("--level",type=int,default=1,help="The level to get the name from. Defaults to 1 i.e. the rundir, 2 would be the dir the rundir is in, etc.")
parser.add_argument("--rundir",type=str,help="the run directory")
parser.add_argument("--event",type=str,help="the string representing the event being run on")
parser.add_argument("--rmbase",type=str,default=None,help="the base runmon directory. If RUNMON_BASE is already in the env variables (and you want to use this as your base), do not pass this")
parser.add_argument("--cluster",type=str,default=None,help="the cluster this is maintained on. This should be fixed, so you should probably just set the RUNMON_CLUSTER env, but this is an alternative if necessary")
parser.add_argument("--envdat",type=str,default=None,help="a path to a single script that sets up the environment, to allow for self healing. If not passed this will not exist, and self-healing cannot be used. If 'generate' is passed as the argument, then it will generate an envsh itself")
opts = parser.parse_args()
   
if opts.rundir != None:
    rd = opts.rundir
else:
    rd = os.getcwd()

if opts.cluster != None:
    cluster = opts.cluster
else:
    cluster = os.environ['RUNMON_CLUSTER']


sto.store(opts.event,rd,level=opts.level,rmbase=opts.rmbase,cluster=cluster,envdat=opts.envdat)
