#!python

import argparse
from runmonitor import check_tools as che

#a script wrapper for the functionality of check_tools.py

parser = argparse.ArgumentParser()
parser.add_argument("--pd",type=str,help="the public directory to write into")
parser.add_argument("--rd",type=str,default=None,help="the run directory, if the public directory is configured already then it can be found in where_on_current_cluster.txt, so need not be passed")
parser.add_argument("--verbose",action="store_true",help="for verbose output")
parser.add_argument("--debug",action="store_true",help="for debugging output")
opts = parser.parse_args()

print(che.update(opts.pd,rd=opts.rd,verbose=opts.verbose,debug=opts.debug))

