#!/usr/bin/env python

#This script takes in a cluster and returns the place to log into for gsissh.

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cluster", required = True, help = "Cluster")
args = parser.parse_args()

cluster_dict = {"CIT": "ldas-pcdev6.ligo.caltech.edu", "LHO": "ldas-pcdev6.ligo-wa.caltech.edu", "LLO": "ldas-pcdev6.ligo-la.caltech.edu"}

print(cluster_dict[args.cluster])
