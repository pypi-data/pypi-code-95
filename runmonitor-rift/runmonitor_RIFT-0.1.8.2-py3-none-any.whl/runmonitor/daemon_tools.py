#!/usr/bin/env python

 

import os
from runmonitor import environ_check
from runmonitor import check_tools as chu
from runmonitor import stat_tools as srd
from runmonitor import update_tools as upa
from runmonitor import restore_tools as resto
#import logging
import time
import daemon
import subprocess
from subprocess import PIPE
from daemon import pidfile


# see: http://www.gavinj.net/2012/06/building-python-daemon-process.html, 
# https://stackoverflow.com/questions/13106221/how-do-i-set-up-a-daemon-with-python-daemon
# https://www.python.org/dev/peps/pep-3143/
# note per https://dpbl.wordpress.com/2017/02/12/a-tutorial-on-python-daemon/ the usage in the first link is deprecated --> trying DaemonContext instead
# https://linuxfollies.blogspot.com/2016/11/linux-daemon-using-python-daemon-with.html


class Main_Daemon():
    def __init__(self, rmdir, cluster="CIT", sender_email="runmonitor.rift.1@gmail.com", receiver=None,
                 password=None, el=False, verbose=False, debug=False, attempt_healing=False, refresh_timer=1800,
                 logging_test = False):
        """
Inputs:
rmdir = the runmon directory

--------
Outputs:
sets up the daemon's attributes (currently not much to do)
        """  
        self.el = el
        self.rmdir = rmdir
        self.cluster = cluster
        self.receiver = receiver
        self.attempt_healing = attempt_healing 
        self.password = password
        self.sender_email = sender_email
        self.log = open(os.path.join(self.rmdir,"daemon/check_daemon.log"),'a')
        self.pidf=os.path.join(self.rmdir,"daemon/check_daemon.pid") 
        self.refresh_timer = refresh_timer
        self.logging_test = logging_test
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
                    events = [os.path.join(self.rmdir,obj) for obj in os.listdir(self.rmdir) if obj != 'daemon' and obj != 'archived_runs_microstatus.txt' and obj != "event_list.txt" and obj != "bad_nodes.txt" and obj != ".ipynb_checkpoints" and obj != "extra_logging.out"]
                runs = []
                #looping over runs
                for event in events:
                    runs = runs + [os.path.join(event,obj) for obj in os.listdir(event)]
                if self.receiver != None and self.password != None:
                    deltas = []
                    print(deltas)
                for run in runs:
                    #checking the time and the job status
                    now = time.asctime(time.gmtime(time.time()))
                    skip_run=False
                    if not os.path.exists(os.path.join(run,"job_status.txt")):
                      chu.update(run)
                    else:
                      lastline = subprocess.check_output(["tail","-n 1",os.path.join(run,"job_status.txt")],text=True).strip()
                      #if the exit was successful or extrinsic_exists exists, it moves on 
                      if lastline.split()[-1] == str(0) or 'extrinsic_exists.txt' in os.listdir(run):
                         print(now + "\t"+"found successful exit, will not update\t"+run)  
                         skip_run=True
                    #otherwise, it updates the logs with chu, and updates the archived_runs_microstatus with upa
                    if not skip_run:
                        print(now + "\t"+"updating logs\t"+run)
                        status = chu.update(run)
                        rundir = chu.read_wocc(run)
                        archive_orig = None
                        if self.receiver != None and self.password != None and os.path.exists(os.path.join(self.rmdir,"archived_runs_microstatus.txt")):
                            with open(os.path.join(self.rmdir,"archived_runs_microstatus.txt"),'r') as f:
                                archive_orig = f.readlines()
                        fullname = run.split("/")[-1]
                        lessername = fullname.split(":")[1]
                        cluster = fullname.split(":")[0]
                        eventname = run.split("/")[-2]
                        

                        resubmit = False # we want to catch various reasons we might want to resubmit
                        force_pass = False

                        with open(os.path.join(run,"job_status.txt"),'r') as f:
                            most_recent_status = f.readlines()[-1]
                        most_recent_status = int(most_recent_status.split()[-1])

                        if most_recent_status == 200000:
                            continue

                        itn = srd.scan_samples(rundir)[4]
                        if self.attempt_healing:
                            cwd = os.getcwd()

                            # Rail Correction
                            import runmonitor.rail_checker as rail                
                            posterior_review = os.path.join(rundir,f"posterior_{itn}_quality.txt") # a file tracking whether correction has happened
                            print("beginning rail check, for iteration "+str(itn))
                            if f"posterior_{itn}_quality.txt" in os.listdir(rundir) or int(itn) == 0:
                                pass
                            else:
                                with open(os.path.join(rundir,"CIP_0.sub"),'r') as f:
                                    original_args = f.readlines()
                                    original_args = [line for line in original_args if "arguments" in line]
                                with open(posterior_review,'w') as f:
                                    f.write("Original Args:\n")
                                    f.writelines(original_args)
                                mc_rail = rail.check_railing(rd=rundir,parameter="mc")
                                eta_rail = rail.check_railing(rd=rundir,parameter="eta")
                                if mc_rail == 0 and eta_rail == 0:
                                    with open(posterior_review,'w') as f:
                                        f.write("No railing found, CIP_arguments unmodified")
                                else:
                                    print("Found railing: MC railing code: "+str(mc_rail))
                                    print("Found railing: eta railing code: "+str(eta_rail))
                                    with open(os.path.join(rundir,"CIP_0.sub"),'r') as f:
                                        new_args = f.readlines()
                                        new_args = [line for line in new_args if "arguments" in line]
                                    with open(posterior_review,'a') as f:
                                        f.write("Modified Args:\n")
                                        f.writelines(new_args)
                                    dag_id = srd.query_dag_id(rundir)
                                    subprocess.Popen(["condor_rm",str(dag_id)],stdout=PIPE,stderr=PIPE)
                                    resubmit=True
                                    time.sleep(15) # a small of amount of time is needed for the rm to go through

                        if most_recent_status == 0 or most_recent_status == 2 or most_recent_status == 200000 or most_recent_status == 100000:
                            run_failed = False
                        else: 
                            run_failed = True
                        
                        if self.attempt_healing and run_failed:
                            from runmonitor import heal
                            envinfo = resto.find_env(run)
                            return_num_jobs = 1
                            idx_test_job = 0
                            error = heal.check_error(rd=rundir,num_returned=return_num_jobs)[idx_test_job]
                            if error == "convert_extr.sub" or error == "resample.sub":
                                return_num_jobs = 30
                                errors = heal.check_error(rd=rundir,num_returned=return_num_jobs)
                                for k,temp_error in enumerate(errors):
                                    if temp_error == "ILE.sub" or temp_error == "ILE_puff.sub" or temp_error == "ILE_extr.sub":
                                        error = temp_error
                                        idx_test_job = k
                                        break
                            if error == "ILE.sub" or error == "ILE_puff.sub" or error == "ILE_extr.sub":
                                jobid = heal.get_job_id(rd=rundir,num_returned=return_num_jobs)[idx_test_job]
                                print(error)
                                print(jobid)
                                #iteration = srd.scan_samples(rundir)[4]
                                #job_id = heal.get_job_id(rd=rundir)
                                gpu_fail = heal.identify_gpu_config_fail(rd=rundir)
                                print(gpu_fail)
                                if gpu_fail != []:
                                    resubmit = True
                                if error == "ILE_extr.sub":
                                    xlal_fail = heal.identify_xlal_fail(rd=rundir,jobid=jobid,iteration=str(int(itn)-1))
                                else:
                                    xlal_fail = heal.identify_xlal_fail(rd=rundir,jobid=jobid,iteration=itn)
                                if xlal_fail:
                                    resubmit = True
                                    jobproc = heal.get_job_procs(rd=rundir,num_returned=return_num_jobs)[idx_test_job]
                                    slot = heal.identify_slot(jobid,jobproc, rd=rundir)
                                    with open(os.path.join(self.rmdir,"daemon","xlal_nodes.txt"),'a') as f:
                                        f.write(f"XLAL fail in {slot}")
                                if self.logging_test:
                                    crasher_fail, num_fails = heal.identify_crasher_fail(rd=rundir,logging_test=self.logging_test)
                                else:
                                    crasher_fail = heal.identify_crasher_fail(rd=rundir)
                                bad_nodes_file = os.path.join(self.rmdir, "bad_nodes.txt")
                                print(crasher_fail)
                                if crasher_fail != []:
                                    resubmit = True
                                if self.logging_test: 
                                    rescue_it = srd.query_last_rescue_num(rd=rundir)
                                    with open(os.path.join(self.rmdir,'extra_logging.out'),'a') as f:
                                        f.write(f"Iteration: {itn}\n")
                                        f.write(f"Rescue #:{rescue_it}\n")
                                        f.write(f"Number of Fails:{num_fails}\n")
                                        f.write(f"Failed Nodes: {crasher_fail}\n")

                                try:
                                    bad_nodes_file_reader = open(bad_nodes_file, "r")
                                    bad_nodes_file_contents = bad_nodes_file_reader.read()
                                    bad_nodes_file_reader.close()
                                except FileNotFoundError:
                                    bad_nodes_file_contents = ""

                                bad_nodes_file_writer = open(bad_nodes_file,"a")
                                for node in crasher_fail:
                                    if node not in bad_nodes_file_contents:
                                        bad_nodes_file_writer.write(node + "\n")
                                bad_nodes_file_writer.close()

                                with open(bad_nodes_file, "r") as f:
                                    lines = f.readlines()
                                    ILE_files = ["ILE.sub", "ILE_extr.sub", "ILE_puff.sub"]
                                    for machine in lines:
                                        machine = machine.strip()
                                        if len(machine) != 0:
                                            for ILE_file in ILE_files:
                                                try:
                                                    ILE_file_handler = open(os.path.join(rundir,ILE_file), "r")
                                                except FileNotFoundError:
                                                    continue
                                                if f'(TARGET.Machine =!= "{machine}")' not in ILE_file_handler.read():
                                                    heal.add_machine_to_requirements(ILE_file, machine, rd=rundir)
                                                ILE_file_handler.close()
                                    f.close()



                            encoding_error = heal.check_encodings_error(rd=rundir,check_node=True)
                            generic_error = heal.check_generic_restart_errors(rd=rundir)
                            if encoding_error or generic_error:
                                resubmit= True
                            if error == "convert_extr.sub" or error == "ILE_extr.sub" or error == "resample.sub":
                                if envinfo == None:
                                    print("Cannot check catjob manually, no environment info is available")
                                else:
                                    heal.detect_and_correct_catjob(rd=rundir,envinfo=envinfo)

                        #resubmit = True # for testing
                        print(f"resubmit = {resubmit}")
                        if resubmit:
                            if envinfo == None:
                                print("Cannot resubmit, no resubmission env available")
                            else:
                                os.chdir(rundir)
                                resto.resubmit(rundir=rundir,force_pass=force_pass,env=envinfo)
                                #resubmit = subprocess.Popen(["python","-c",
                                #    f"import runmonitor.restore_tools as resto; resto.resubmit(rundir='{rundir}',force_pass='{force_pass}')"],
                                #    text=True,stdout=PIPE,stderr=PIPE,env=envinfo)
                                #resubmit = subprocess.Popen(["/bin/bash","-c","source "+env,"&&","python","-c",
                                #   "'import restore_tools as resto; resto.resubmit(rundir="+rundir+",fp="+str(force_pass)+")'"],
                                #   text=True,stdout=PIPE,stderr=PIPE)
                                os.chdir(cwd)
                            status = chu.update(run)

                        upa.update(lessername,eventname,self.rmdir,cluster)

                        if self.receiver != None and self.password != None and archive_orig != None: 
                            with open(os.path.join(self.rmdir,"archived_runs_microstatus.txt"),'r') as f:
                                archive_now= f.readlines()
                            for i,line in enumerate(archive_now):
                                if line != archive_orig[i]:
                                    deltas += [line]
                            print(deltas)

                if self.receiver != None and self.password != None and deltas != []:
                    #TODO emailing
                    import smtplib, ssl
                    smtp_server = "smtp.gmail.com"
                    port = 587
                    email_context = ssl.create_default_context()
                    try:
                        server = smtplib.SMTP(smtp_server,port)
                        server.ehlo()
                        server.starttls(context=email_context)
                        server.ehlo()
                        server.login(self.sender_email,self.password)
                        message = "Subject: runmonitor-rift updates \n\n\n \
                        You are receiving an automated email from runmonitor regarding your current runs on "+self.cluster+". If you do not wish to receive these emails please, dis-instantiate this daemon. If you did not instatiate this daemon, please contact rudall@caltech.edu. The following lines were found to have changed in your archived_run_microstatus.txt, indicating a state change for the run:\n"+" \n".join(deltas)
                        server.sendmail(self.sender_email,self.receiver,message)
                        print("sent email to "+self.receiver)
                    except Exception as fail:
                        print("failed to send email")
                        print(fail) 
                      
                #finally, it waits for the designated amount of time to rerun
                time.sleep(self.refresh_timer)
