#!python

#This takes in a run and event (along with the base and cluster environment variables that you have to pass in) and added the appropriate information to archived_runs_microstatus.txt. May be good to call when creating a new run.
import argparse
from runmonitor import update_tools as upa
import os

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--run", required = True, help = "The run you want to add")
parser.add_argument("-e", "--event", required = True, help = "The event the run is on")
parser.add_argument("-b", "--base", help = "Runmon base")
parser.add_argument("-c", "--cluster", help = "Runmon cluster")
args = parser.parse_args()

if args.base == None:
    base = os.environ['RUNMON_BASE']
else:
    base = args.base
if args.cluster == None:
    cluster = os.environ['RUNMON_CLUSTER']
else:
    cluster = args.cluster
    
upa.update(args.run,args.event,base,cluster)

