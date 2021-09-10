#!/usr/bin/env python
#Reads dagman.out to see what the latest error is by iterating backwards through it. It's run in the run directory.

linelist = []

dagman = open("marginalize_intrinsic_parameters_BasicIterationWorkflow.dag.dagman.out")
dag_list = dagman.readlines()[::-1]
dagman.close()

for line in dag_list:
	linelist.append(line)
	if ("ERROR: the following job(s) failed" in line):
		break
	else:
		if (len(linelist) > 12):
			linelist.pop(0)

linelist = linelist[::-1]
error_file = linelist[8].split()[5].strip()

print(error_file)
