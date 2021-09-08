#!/usr/bin/env python


import os
import shutil


def force(wd=None,fname=None,verbose=False,debug=False):
    """
Inpupts:
-------------
wd = working directory, if none will take cwd
fname = name of rescue to force pass, if None will find the most recent marg*.dagman.rescue0nn

Outputs:
----------
The input *.rescue is renamed to *.rescue0nn_original, while a new rescue with the original name is created which has skipped over the given jobs

    """ 



    if wd == None:
        wd = os.getcwd()
    if fname == None:
        rescues = [el for el in os.listdir(wd) if "original" not in el and "rescue" in el] 
        rescues = sorted(rescues, key=lambda x: x.split(".")[-1])
        if debug:
            print(rescues)
        fname = rescues[-1]

    ofile = wd+"/"+fname
    nfile = wd+"/"+"overwrite_"+fname

    shutil.copyfile(ofile,nfile)

    with open(ofile) as fp:
        contents = fp.readlines()
    failed_nodes = contents[8]

    failed_nodes = failed_nodes.strip("#")
    failed_nodes = failed_nodes[:-11]
    failed_nodes = failed_nodes.strip()

    failed_nodes = failed_nodes.split(",")
    contents.insert(8,"")
    for i in range(len(failed_nodes)):
        insertion_element = "DONE " + str(failed_nodes[i])+"\n"
        if verbose:
            print(insertion_element)
        contents.insert(10,insertion_element)
    if verbose:
        print(contents)
    with open(nfile,'w') as f:
        f.writelines("%s" % line for line in contents)
    shutil.move(ofile,ofile+"_original")
    shutil.move(nfile,ofile)

