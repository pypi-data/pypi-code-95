import os
from runmonitor import stat_tools as stt

def compile_done_dag_lines(daglinelist):
    # a helper function
    dones = []
    for i,line in enumerate(daglinelist):
        if "JOB" in line:
            node = line.split()[1]
            dones+= ["DONE "+node+"\n"]
    return dones




def construct_rescue(basedir=None):
    """
Inputs:
basedir = where to run, if not local

Outputs:
None, creates a rescue file labelled manual_rescue, which should be renamed as appropriate
    """
    if not basedir:
        basedir = os.getcwd()
    files = os.listdir(basedir)
    overlaps = [f for f in files if "overlap-grid" in f and ".xml.gz" in f]
    overlaps = sorted(overlaps,key =lambda x: x.split('-')[-1].split(".")[0])
    last_finished_it = overlaps[-1].split('-')[-1].split(".")[0]
    next_it = str(int(last_finished_it)+1)
    dag_prefix,_ = stt.determine_dag_prefix_and_run_status(basedir)
    with open(os.path.join(basedir,dag_prefix+".dag"),'r') as f:
        daglines = f.readlines()
    conditional_start = None
    terminus = 0
    if f"consolidated_{next_it}.composite" in files:
        # A CIP failure
        for i,line in enumerate(daglines):
            if f'macroiteration="{next_it}"' in line and "CIP" in daglines[i+1]:
                terminus = i-2
                break
        if terminus == 0:
            print("found no nextit")
    else:
        # we'll assume an ILE failure, actually robust even if not because it will autolist all ILEs as complete then move on
         for i,line in enumerate(daglines):
            if f'macroiteration="{next_it}"' in line and 'macroevent="0"' in line:
                    if "PUFF" in daglines[i-7] and f"puffball-{last_finished_it}.xml.gz" not in files:
                        terminus = i-7
                    else:
                        conditional_start = i -2
            if f'macroiteration="{next_it}"' in line and "join" in daglines[i+1]:
                terminus = i+1
                break
         if terminus == 0:
             print("found no nextit")
    if not conditional_start:
        completed = compile_done_dag_lines(daglines[:terminus])
    else:
        completed = compile_done_dag_lines(daglines[:conditional_start])
        conditional_lines = daglines[conditional_start:terminus]
        ileouts = os.listdir(os.path.join(basedir,"iteration_"+next_it+"_ile/"))
        for i,line in enumerate(conditional_lines):
            if "macroevent" in line:
                macroevent = line.split()[2][-2]
                for el in ileouts:
                    if "CME_out-"+macroevent in el:
                        completed += ["DONE "+line.split()[1]+"\n"]
                        break
             
    with open("manual_rescue",'w') as f:
        f.write("# Manually generated rescue dag\n")
        f.writelines(completed)
            



construct_rescue("/home/richard.udall/Injection_Study/Injection_PE/GT0010_NSBH/GT0010_NSBH-SEOBNRv4_ROM_NSBH-pins-batch-test")

    
