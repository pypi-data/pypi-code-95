#!/usr/bin/env python

#This script takes in a cluster and returns the place to log into for gsissh.

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cluster", default = None, help = "Cluster")
args = parser.parse_args()

cluster_dict = {"CIT": "ldas-pcdev6.ligo.caltech.edu", "LHO": "ldas-pcdev6.ligo-wa.caltech.edu", "LLO": "ldas-pcdev6.ligo-la.caltech.edu"}

if args.cluster == None:
    import os
    cluster = os.environ['RUNMON_CLUSTER']
else:
    cluster = args.cluster

print(cluster_dict[cluster])
