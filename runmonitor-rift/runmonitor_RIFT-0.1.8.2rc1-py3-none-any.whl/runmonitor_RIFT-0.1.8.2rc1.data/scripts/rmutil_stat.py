#!python

# a script wrapper for stat_tools, produces run directory status updates.

import argparse
from runmonitor import stat_tools as sta

parser = argparse.ArgumentParser()
parser.add_argument("--verbose",action='store_true',help="pass for verbose output")
parser.add_argument("--rd",type=str,help="the run directory being scanned, absolute path")
parser.add_argument("--debug",action='store_true',help="pass for debug information")
opts = parser.parse_args()    

print(sta.scan_samples(opts.rd,debug=opts.debug,verbose=opts.verbose))
print(sta.query_dag_exit(opts.rd,debug=opts.debug,verbose=opts.verbose))
print(sta.query_dag_id(opts.rd,debug=opts.debug,verbose=opts.verbose))
