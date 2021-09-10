#!/usr/bin/env python

import os
import glob
from subprocess import PIPE, Popen
from runmonitor import stat_tools as stt


def check_error(rd=None,num_returned = 1):
	linelist = get_linelist(rd, num_errors = num_returned)
	error_files = []
	for i in range(num_returned):
		error_files += [linelist[7+11*i].split()[5].strip()]
	return error_files

def get_job_id(rd=None, num_returned = 1):
	linelist = get_linelist(rd,num_errors=num_returned)
	job_ids = []
	for i in range(num_returned):
		job_ids += [linelist[6+11*i].split()[5].split(".")[0].strip("(").strip()]
	return job_ids

def get_job_procs(rd=None, num_returned = 1):
	linelist = get_linelist(rd,num_errors=num_returned)
	job_procs = []
	for i in range(num_returned):
		job_procs += [linelist[6+11*i].split()[5].split(".")[1].strip("(").strip()]
	return job_procs

def get_linelist(rd=None,num_errors=1):
	"""
	Inputs:
	---------
	rd = rundir, if not given will default to cwd
	num_errors = number of individual failed job lines to return; each failed job consists of 10 lines. 
	These are started from the top of the list, assuming failures will occur for homogeneous reasons
	If the value passed for num_errors is not an int it will return all of the failures instead

	Outputs:
	----------
	A list containing the lines of the first num_errors error messages in the .dagman.out

	"""
	#setup
	linelist = []
	if (rd == None):
		rd = os.getcwd()

	#generalized against non-standard dag names
	dag_prefix, _ = stt.determine_dag_prefix_and_run_status(rd)
	dagman = open(os.path.join(rd,dag_prefix+".dag.dagman.out"))
	dag_list = dagman.readlines()[::-1]
	dagman.close()

	#count back till we find the start of the rror messages
	for line in dag_list:
		linelist.append(line)
		if ("ERROR: the following job(s) failed" in line):
			break
	#order front to back
	linelist = linelist[::-1]
	#each error code is 11 lines long, so if num_errors is an int this will get you num_errors number of error codes
	if type(num_errors) == int:
		linelist = linelist[1:11*num_errors+2]
	else: # if num_errors is not an error code, this will go till it finds the end of the error codes, then cut linelist there
		linelist = linelist[1:]
		for j,line in enumerate(linelist):
			if "<END>" in line: #<END> appears in the last separator of the error codes
				linelist = linelist[:j]
				break
	return linelist

def check_effective_samples_error(iteration,rd=None):
	import glob
	import sys

	if rd == None:
		rd = os.getcwd()

	filename = glob.glob(rd+"/iteration_" + str(iteration) + "_cip/logs/cip*.err")[0]
	err = open(filename)
	err_lines = err.readlines()
	err.close()

	for item in err_lines[::-1]:
        	if ("Effective samples = nan" in item):
                	print(True)
                	return True
	print(False)
	return False

def get_ile_job(rd=None):
	check_error(rd)

def identify_slot(process_id,process,rd=None):
	if rd == None:
		rd = os.getcwd()

	for root, dirs, files in os.walk(rd,followlinks=True):
		for name in files:
			fname = os.path.join(root,name)
			if str(process_id) in fname and f"-{process}.log" in fname:
				try:
					with open(fname,'r') as f:
						lines = f.readlines()[::-1]
					for i,line in enumerate(lines):
						if "Job executing on host" in line:
							subparts = line.split("&")
							for subpart in subparts:
								if "alias=" in subpart:
									node = subpart.split("=")[1]
							return node
				except Exception as fail:
					return None
	return None


"""
	#another old attempt
	print(os.getcwd())
	cmd = f"find -name {rd}/*{process_id}*"
	pipe = Popen(cmd,stdout=PIPE,shell=True)
	files = pipe.communicate() #produces a tuple or out,error
	os.chdir(odir)
	print(os.getcwd())
	try: #this sometimes fails for reasons I am not super clear on, so I try excepted it accordingly
		files = files[0].strip() #takes the out part
		files = str(files).split("\\n")
		for fname in files:
			if ".log" in fname and f"-{process}." in fname: 
				fpath = os.path.join(rd,fname)
		with open(fpath,'r') as f:
			lines = f.readlines()[::-1]
		for i,line in enumerate(lines):
			if "Job executing on host" in line:
				subparts = line.split("&")
				print(subparts)
				for subpart in subparts:
					if "alias=" in subpart:
						node = subpart.split("=")[1]
				print(fpath,node)
				return node
	except:
		return None

	#old attempt
	cmd = ["condor_history",process_id,"-limit","1","-af","LastRemoteHost"] #command courtesy of James Clark
	histpipe = Popen(cmd,stdout=PIPE,stderr=PIPE)
	out,err = histpipe.communicate()
	return out
	"""

def check_generic_restart_errors(rd=None):
	import sys
	
	if rd == None:
		rd = os.getcwd()
             
	error_list = get_linelist(rd,num_errors=None)
	for i,line in enumerate(error_list):
		# some random errors that generally should just be resubmitted through
		if "Node return val: 62" in line or "Node return val: -7" in line or "Node return val: 91" in line \
			or "Node return val: -6" in line or "Node return val: 126" in line:
			return True
	return False
			

def check_encodings_error(rd=None,check_node=False):
	import sys
	
	if rd == None:
		rd = os.getcwd()
             
	error_list = get_linelist(rd,5)
	failids = []
	for i,line in enumerate(error_list):
		# return val -6 = encodings error (it seems? I don't know where that would be coded)
		if "Node return val: 134" in line:
			# The next line has, e.g.:  12/06/20 15:06:05           Error: Job proc (67422388.0.0) failed with status 35
			idline = error_list[i+1]
			failid_info = idline.split("(")[1].split(")")[0].split(".")
			failid = failid_info[0] # hacky string parsing, assuming no other parentheses
			process = failid_info[1]
			failids += [(failid,process)]

	if check_node and failids != []:
		failslots = []
		for root, dirs, files in os.walk(rd,topdown=True,followlinks=True):
			for name in files:
				for failid in failids:
					if failid[0] in name:
						err = open(os.path.join(root,name))
						err_lines = err.readlines()
						err.close()

						for item in err_lines[::-1]:
							if ("No module named 'encodings'" in item):
								process = fname.split(".")[0].split("-")[-1]
								failslots += [identify_slot(failid,process,rd=rd)]
								continue
		print(failslots)
		return True
	elif failids != []:
		return True
	else:
		return False




	""" filenames = glob.glob(rd+"/iteration_" + str(iteration) + "_ile/logs/ILE*" + str(job_id) + "*.err")

	for fname in filenames:
		err = open(fname)
		err_lines = err.readlines()
		err.close()

		for item in err_lines[::-1]:
			if ("No module named 'encodings'" in item):
				print(True)
				if check_node:
					process = fname.split(".")[0].split("-")[-1]
					print(identify_slot(job_id,process))
				return True
	print(False)
	return False """

#add_req(rd,slot)

def identify_gpu_config_fail(rd=None):
	if rd == None:
		rd = os.getcwd()

	#get some representative errors
	#5 is just a random value; the issue is that usually virtually all of the fails will be because of a single blackhole
	#this way we have a chance to catch more; one could do all of them but condor_history is a slow command
	#after a bit of testing, this works pretty well
	error_list = get_linelist(rd,num_errors=None)
	failids = []
	gpu_fail_slots = []

	for i,line in enumerate(error_list):
		# return val 35 = no cupy error
		if "Node return val: 35" in line:
			# The next line has, e.g.:  12/06/20 15:06:05           Error: Job proc (67422388.0.0) failed with status 35
			idline = error_list[i+1]
			failid_info = idline.split("(")[1].split(")")[0].split(".")
			failid = failid_info[0] # hacky string parsing, assuming no other parentheses
			process = failid_info[1]
			failids += [(failid,process)]

	for failid in failids:
		failslot = identify_slot(failid[0],failid[1],rd=rd)# see above
		print(failslot)
		if failslot not in gpu_fail_slots and failslot != None:
			gpu_fail_slots += [failslot]

	return gpu_fail_slots

def identify_crasher_fail(rd=None,logging_test = False):
	if rd == None:
		rd = os.getcwd()


	error_list = get_linelist(rd,num_errors=None) #I think we don't pass an int here because it won't be a single black hole node causing issues - we want to avoid many
	failids= []
	crasher_fail_slots = []

	for i,line in enumerate(error_list):
		# return val 9 = run crasher killed it
		if "Node return val: 9" in line:
			# The next line has, e.g.:  12/06/20 15:06:05           Error: Job proc (67422388.0.0) failed with status 35
			idline = error_list[i+1]
			failid_info = idline.split("(")[1].split(")")[0].split(".")
			failid = failid_info[0] # hacky string parsing, assuming no other parentheses
			process = failid_info[1]
			failids += [(failid,process)]

	for failid in failids:
		failslot = identify_slot(failid[0],failid[1],rd=rd)# see above
		if failslot not in crasher_fail_slots:
			crasher_fail_slots += [failslot]

	if logging_test:
		return crasher_fail_slots, len(failids)
	else:
		return crasher_fail_slots

#Instead of returning - the idea in mattermost is to write to a file. Is it possible to just run
#the requirement-adding script here with something like addreq.py --avoid-machine crasher_fail_slots

def check_frequency_error(iteration,job_id,rd=None):
	import glob
	import sys

	if rd == None:
		rd = os.getcwd()

	filename = glob.glob(rd+"/iteration_" + str(iteration) + "_ile/logs/ILE*" + str(job_id) + "*.err")[0]
	err = open(filename)
	err_lines = err.readlines()
	err.close()

	for item in err_lines[::-1]:
        	if ("Initial frequency is too high" in item):
                	print(True)
                	return True
	print(False)
	return False

def check_mc_range_error(rd=None):
	import glob
	import sys

	if rd == None:
		rd = os.getcwd()

	filename = glob.glob(rd+"/iteration_" + str(iteration) + "_cip/logs/cip*.err")[0]
	err = open(filename)
	err_lines = err.readlines()
	err.close()

	for item in err_lines[::-1]:
        	if not ("Points used in fit" in item):
                	print(True)
                	return True
	print(False)
	return False

def count_fails(rd=None):
	if rd == None:
		rd = os.getcwd()

	linelist = get_linelist(rd,num_errors=None)
	return int(len(linelist)/11) # 11 lines per error, cast to int in case bookends make the total number of lines mod 11 != 0
	

def find_max_extr_possible(rd=None):
	if rd == None:
		rd = os.getcwd()

	os.chdir(rd)
	# find the next to last iteration directory which, for reasons, is where the extrinsic jobs generate
	cmd = "ls | grep '_ile' | sort -n -t '_' -k2 | tail -n2 | head -n1"
	pipe = Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
	extr_dir, err = pipe.communicate()
	extr_dir = str(extr_dir)
	extr_dir = extr_dir[2:-3]
	extr_dir = os.path.join(rd,str(extr_dir))
	os.chdir(extr_dir)
	#print(os.getcwd())
	# a very convoluted set of commands to extract the point numbers from e.g. EXTR_out-980.xml_9_.xml.gz
	# Then sort by those numbers to find the largest
	# this tells us the 
	cmd = "ls | grep '.xml.gz' | tr '-' ' ' | tr '.' ' ' | awk '{print $2}' | sort -n | tail -n1"
	pipe = Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
	out, err = pipe.communicate()
	return int(out)

def detect_and_correct_catjob(rd=None, thres_frac = 1. / 40.,envinfo=None):
	num_fails = count_fails(rd=rd)
	max_extr_possible =find_max_extr_possible(rd=rd)
	threshold = max_extr_possible * thres_frac # corresponds to 200 for an 8000 point run - should finetune / allow user to set
	if num_fails < threshold:
		cwd = os.getcwd()
		os.chdir(rd)
		cmd = "./catjob.sh"
		catproc = Popen(cmd,stdout=PIPE,stderr=PIPE,env=envinfo)
		print(catproc.stderr.read())
		print(catproc.stdout.read())
		os.chdir(cwd)

def identify_xlal_fail(rd=None,jobid=None,iteration=None):
	# to catch annoying transient xlal failures
	if jobid == None or iteration == None:
		return False
	if rd == None:
		rd = os.getcwd()

	try:
		# see encodings error
		filename = glob.glob(rd+"/iteration_" + str(iteration) + "_ile/logs/ILE*" + str(jobid) + "*.err")[0]
		with open(filename,'r') as err:
			err_lines = err.readlines()
	except Exception as e:
		print(e)
		return False

	for line in err_lines:
		# use two separate lines just as a double check - should always catch on the first one
		if "XLAL Error - XLALFrameUFrFileOpen_FrameL_ (LALFrameL.c:187): FrFileINew failed." in line: 
			return True
		elif "XLAL Error - XLALFrameUFrFileOpen_FrameL_ (LALFrameL.c:187): I/O error" in line:
			return True
	
	return False


def add_machine_to_requirements(filename,addition,rd=None):
	if rd == None:
		rd = os.getcwd()

	with open(os.path.join(rd,filename),'r') as f:
		lines = f.readlines()
	
	reqstr = f'(TARGET.Machine =!= "{addition}")'

	for j,line in enumerate(lines):
		if "requirements =" in line:
			reqline = line
			reqline_idx = j
	if ")" not in reqline:
		reqline = reqline.replace("\n",reqstr+"\n")
	else:
		reqline = reqline.replace("requirements = ",f"requirements = {reqstr}&&")
	
	lines[reqline_idx] = reqline
	with open(os.path.join(rd,filename),'w') as f:
		f.writelines(lines)
