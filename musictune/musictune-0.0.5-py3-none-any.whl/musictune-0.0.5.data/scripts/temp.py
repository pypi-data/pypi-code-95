import subprocess
import time

proc = subprocess.Popen(['start_cluster.py'], shell=True)
time.sleep(5)
pid = proc.pid

print(pid)