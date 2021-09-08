#!/usr/bin/env python

import os
from runmonitor import daemon_tools as dae
import argparse

#a script wrapper for the daemon initialization - call without arguments to activate default daemon behavior

parser = argparse.ArgumentParser()
parser.add_argument("--rmdir",default=None,type=str,help="The run monitoring ddirectory, defaults to the contents of environment variable RUNMON_BASE")
parser.add_argument("--verbose",action="store_true")
parser.add_argument("--debug",action="store_true")
parser.add_argument("--sender-email",type=str,default="runmonitor.rift.1@gmail.com")
parser.add_argument("--receiver",type=str,default=None,help="the email that updates on runmon should be sent to")
#parser.add_argument("--password",type=str,default=None,help="the password for the sender email; if using the default sender email, you can get this from the git.ligo.org wiki for runmonitor")
#having password as a flag was even more ludicrously insecure than the rest of this, since the flag shows up under a ps -ef; it is now replaced by a request for input on startup
parser.add_argument("--event-list",action='store_true',help="pass to have the daemon run through a list of event directories labelled event_list.txt in the RUNMON_BASE, rather than trying to guess at them itself")
parser.add_argument("--attempt-healing",action='store_true',help="If passed, the daemon will attempt automated healing")
parser.add_argument("--refresh-timer",type=int,default=1800,help="The interval to do updates on, in an integer number of seconds. Default is 1800 s = 1 half hour. Faster may be good for e.g. restarting after gpu fails")
parser.add_argument("--logging-test",action = 'store_true', help = "If passed, produces an extra logging file for runcrasher")
opts = parser.parse_args()
    
#can pass no arguments and it will pick up on your RUNMON_BASE env
if opts.rmdir == None:
    rmdir = os.environ["RUNMON_BASE"]
else:
    rmdir = opts.rmdir
print("starting daemon")  
          
#If an email address to receive messages is given, ask for input
password = None
if opts.receiver != None:
    password = input("Please give the password for the email address you wish to use")

#starting up the daemon
cdaemon = dae.Main_Daemon(rmdir, attempt_healing=opts.attempt_healing, el=opts.event_list, verbose=True, debug=True, sender_email=opts.sender_email,receiver=opts.receiver,password=password,refresh_timer=opts.refresh_timer,logging_test = opts.logging_test)
cdaemon.summon()

