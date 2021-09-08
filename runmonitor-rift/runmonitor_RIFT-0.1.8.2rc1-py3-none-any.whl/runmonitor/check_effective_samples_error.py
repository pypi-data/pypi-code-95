#!/usr/bin/env python
#Gets the current iteration, enters the folder, and reads the cip .err file to see if the effective samples error is present. The only argument is --iteration, which is the iteration the run is on. It's run in the run directory.

import argparse
import glob
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iteration", required = True, help = "What iteration the run is on")
args = parser.parse_args()

filename = glob.glob("iteration_" + args.iteration + "_cip/logs/cip*.err")[0]
err = open(filename)
err_lines = err.readlines()
err.close()

for item in err_lines[::-1]:
	if ("Effective samples = nan" in item):
		print(True)
		sys.exit()
print(False)
