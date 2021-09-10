#!/usr/bin/env python

import argparse
from runmonitor import dagpass

# a script wrapper for the dag forced continuation functionality 

parser=argparse.ArgumentParser()
parser.add_argument("--fname",type=str,default=None,help="The name of the rescue to do the overwrite to. For Safety, rather than writing to this file, it will be copied and that will be operated on. This file is overwrite_{fname}")
parser.add_argument("--debug",action='store_true')
parser.add_argument("--verbose",action="store_true")
parser.add_argument("--wd",type=str,default=None,help="the working directory to do a force pass in")
opts = parser.parse_args()

dagpass.force(fname=opts.fname,wd=opts.wd,debug=opts.debug,verbose=opts.verbose)

