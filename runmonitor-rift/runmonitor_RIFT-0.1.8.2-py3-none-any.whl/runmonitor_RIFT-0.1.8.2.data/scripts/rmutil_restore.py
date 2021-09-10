#!python

import os
from runmonitor import environ_check
from runmonitor import restore_tools as res

#a script wrapper for restore_tools; still a WIP

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",action='store_true')
    parser.add_argument("--debug",action='store_true')
    parser.add_argument("--rmdir",type=str,help="the run monitoring directory for the analysis, defaults to cwd")
    opts = parser.parse_args()
    
    if opts.rmdir == None:
        rmdir = os.getcwd()
    else:
        rmdir = opts.rmdir

    print(rmdir) 
   
    if opts.debug:
        print(res.find_env(rmdir,verbose=opts.verbose,debug=opts.debug))
    
    res.resubmit(rmdir,debug=opts.debug,verbose=opts.verbose)
