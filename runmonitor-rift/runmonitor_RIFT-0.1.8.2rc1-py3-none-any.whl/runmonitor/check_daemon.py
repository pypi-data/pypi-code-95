#!/usr/bin/env python

 

import os
from runmonitor import check_up as chu
from runmonitor import stat_rd as srd
from runmonitor import update_archive as upa
#import logging
import time
import daemon
import subprocess
from daemon import pidfile


# see: http://www.gavinj.net/2012/06/building-python-daemon-process.html, 
# https://stackoverflow.com/questions/13106221/how-do-i-set-up-a-daemon-with-python-daemon
# https://www.python.org/dev/peps/pep-3143/
# note per https://dpbl.wordpress.com/2017/02/12/a-tutorial-on-python-daemon/ the usage in the first link is deprecated --> trying DaemonContext instead
# https://linuxfollies.blogspot.com/2016/11/linux-daemon-using-python-daemon-with.html


class Main_Daemon():
    def __init__(self,rmdir,el=False,verbose=False,debug=False):
        """
Inputs:
rmdir = the runmon directory

--------
Outputs:
sets up the daemon's attributes (currently not much to do)
        """  
        self.el = el
        self.rmdir = rmdir
        self.log = open(os.path.join(self.rmdir,"daemon/check_daemon.log"),'a')
        self.pidf=os.path.join(self.rmdir,"daemon/check_daemon.pid") 
        """
        using logging package was running into weird OS errors when in DaemonContext, so for now we'll us the inelegant method of just printing to stdout
        self.logger = logging.getLogger('check_daemon')
        self.logger.setLevel(logging.INFO) 
        self.logf = os.path.join(rmdir,"daemon/daemon.log")       
        fh = logging.FileHandler(self.logf)
        fh.setLevel(logging.INFO)
        formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(formatstr)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        """
  
    def summon(self):
        """
inputs:
---------
self

outputs:
---------
Periodically uses check_up.py on all of the public directories, skipping if extrinsic_exists is present or job_status == 0

        """
        #creating the information associated with the daemon
        context = daemon.DaemonContext(stdout = self.log,stderr=self.log,working_directory=self.rmdir,pidfile=pidfile.TimeoutPIDLockFile(self.pidf),umask=0o002)  
        #entering the daemon
        #all prints write to stdout now, and all errors go to stderr
        with context:       
           while True:   
                print("starting update cycle")
                #assuming base/event/run hierarchy, and skipping over the files we know are not events
                #RUNMON should be kept clean, or we should actually keep track of the events (a dedicated textfile maybe?)
                if self.el:
                    with open(os.path.join(self.rmdir,"event_list.txt")) as f:
                        events = [ob.strip("\n") for ob in f.readlines()]
                else:
                    events = [os.path.join(self.rmdir,obj) for obj in os.listdir(self.rmdir) if obj != 'daemon' and obj != 'archived_runs_microstatus.txt']
                runs = []
                #looping over runs
                for event in events:
                    runs = runs + [os.path.join(event,obj) for obj in os.listdir(event)]
                for run in runs:
                    #checking the time and the job status
                    now = time.asctime(time.gmtime(time.time()))
                    skip_run=False
                    if not os.path.exists(os.path.join(run,"job_status.txt")):
                      skip_run=False
                    else:
                      lastline = subprocess.check_output(["tail","-n 1",os.path.join(run,"job_status.txt")],text=True).strip()
                      #if the exit was successful or extrinsic_exists exists, it moves on 
                      if lastline.split()[-1] == str(0) or 'extrinsic_exists.txt' in os.listdir(run):
                         print(now + "\t"+"found successful exit, will not update\t"+run)  
                         skip_run=True
                    #otherwise, it updates the logs with chu, and updates the archived_runs_microstatus with upa
                    if not skip_run:
                        print(now + "\t"+"updating logs\t"+run)
                        chu.update(run)
                        fullname = run.split("/")[-1]
                        lessername = fullname.split(":")[1]
                        cluster = fullname.split(":")[0]
                        eventname = run.split("/")[-2]
                        upa.update(lessername,eventname,self.rmdir,cluster)
                #finally, it waits 1 hour befor updating again
                time.sleep(3600)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rmdir",default=None,type=str,help="The run monitoring ddirectory, defaults to the contents of environment variable RUNMON_BASE")
    parser.add_argument("--verbose",action="store_true")
    parser.add_argument("--debug",action="store_true")
    parser.add_argument("--event-list",action='store_true',help="pass to have the daemon run through a list of event directories labelled event_list.txt in the RUNMON_BASE, rather than trying to guess at them itself")
    opts = parser.parse_args()
    
    #can pass no arguments and it will pick up on your RUNMON_BASE env
    if opts.rmdir == None:
        rmdir = os.environ["RUNMON_BASE"]
    else:
        rmdir = opts.rmdir
    print("starting daemon")  
          
    #starting up the daemon
    cdaemon = Main_Daemon(rmdir,el=opts.event_list, verbose=True,debug=True)
    cdaemon.summon()
