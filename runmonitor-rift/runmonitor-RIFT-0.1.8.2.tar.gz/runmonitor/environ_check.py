import os

try:
    if os.environ["RUNMON_BASE"] != "":
        print("RUNMON_BASE == "+os.environ["RUNMON_BASE"])
    else:
        print("RUNMON_BASE is blank, this will likely end badly")
except:
    print("RUNMON_BASE is not set, this will likely end badly")

try:
    if os.environ["RUNMON_CLUSTER"] != "":
        print("RUNMON_CLUSTER == "+os.environ["RUNMON_CLUSTER"])
    else:
        print("RUNMON_CLUSTER is blank, this will likely end badly")
except:
    print("RUNMON_CLUSTER is not set, this will likely end badly")
