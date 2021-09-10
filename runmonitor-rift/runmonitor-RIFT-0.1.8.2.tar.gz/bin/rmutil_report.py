#!/usr/bin/env python

#This script first begins by checking archived_runs_microstatus.txt to see if the run exists. From there, it grabs all the information necessary. It takes convergence and run description from the file structure, and job status and run path from archived_runs_microstatus.txt. Lastly, it writes all the info to stdout.

import argparse
import sys
import os
from runmonitor import environ_check
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--run", required = True, help = "The run you want to get a report for")
parser.add_argument("-b", "--base", default = None, help = "Runmon base")
parser.add_argument("-c", "--cluster", default = None, help = "Runmon cluster")
args = parser.parse_args()

if args.base == None:
    base = os.environ['RUNMON_BASE']
else:
    base = args.base 
if args.cluster == None:
    cluster = os.environ['RUNMON_CLUSTER']
else:
    cluster = args.cluster

runs = open(base + "/archived_runs_microstatus.txt")
run_list = runs.readlines()
runs.close()

for item in run_list:
	item_list = item.split("\t")
	run = item_list[0]
	if (run == args.run):
		try:
			event = item_list[1]
			runpath = base + "/" + event + "/" + cluster + ":" + run

			convergence_file = open(runpath + "/convergence.txt")
			convergence_info = convergence_file.readlines()[-1]
			convergence_file.close()
			convergence_list = convergence_info.split("\t")
			if (convergence_list[2] == "10000000"):
				convergence_list[2] = "-"

			dag_id_file = open(runpath + "/dag_id.txt")
			dag_id = dag_id_file.read().strip()
			dag_id_file.close()

			path_of_run = item_list[2]

			job_status = item_list[3].strip()

			run_desc = "-"
			if (os.path.isfile(runpath + "/run_description.txt")):
				run_desc_file = open(runpath + "/run_description.txt")
				run_desc = run_desc_file.read().strip()
				run_desc_file.close()

			extrinsic_exists = "No"
			extrinsic_points = "0"
			if (os.path.isfile(runpath + "/extrinsic_exists.txt")):
				extrinsic_exists = "Yes"
				extrinsic_file = open(runpath + "/extrinsic_exists.txt")
				extrinsic_points = extrinsic_file.read().strip()
				extrinsic_file.close()

			now = datetime.now()
			current_time = now.strftime("%m/%d/%Y_%H:%M:%S")

			#if run report already exists, then add on to existing report
			sys.stdout.write(current_time + "\t" + event + "\t" + run + "\t" + path_of_run + "\t" + dag_id + "\t" + job_status + "\t" + convergence_list[1] + "\t" + convergence_list[2] + "\t" + convergence_list[3].strip() + "\t" + extrinsic_exists + "\t" + extrinsic_points + "\t" + run_desc)
		except IOError as e:
			print("Error: Run " + run + " found in archive but not in file structure")
		sys.exit()

print("Run " + args.run + " Not Found")
