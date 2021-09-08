#!python

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--base", default = None, help = "Runmon base")
args = parser.parse_args()

if args.base == None:
    base = os.environ['RUNMON_BASE']
else:
    base = args.base

eventlist = open(base + "/event_list.txt")
events = eventlist.readlines()
eventlist.close()

for event in events:
	print(event)
