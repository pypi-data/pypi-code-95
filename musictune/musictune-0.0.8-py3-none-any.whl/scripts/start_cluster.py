import os
import subprocess
import sys
import time
from os.path import expanduser


def main():
    home = expanduser("~")
    scheduler_path = os.path.join(home, 'scheduler.json')
    if len(sys.argv[1:]) > 0:
        no_of_workers = int(sys.argv[1])
    else:
        val = input("Enter number of workers (4-24):")
        no_of_workers = int(val)
    sch_file = os.path.join(home, 'scheduler.json')
    if os.path.isfile(sch_file):
        print("A scheduler.json file already exists - removing it")
        os.remove(sch_file)
    os.system('killall -r dask-scheduler')
    os.system('killall -r dask-worker')
    scheduler = subprocess.Popen([f"dask-scheduler --scheduler-file {scheduler_path} --idle-timeout 600"],
                                 shell=True)
    time.sleep(2)
    workers = []
    for i in range(no_of_workers):
        workers.append(
            subprocess.Popen([f"dask-worker --nthreads 4 --scheduler-file {scheduler_path} --local-directory $TMP"],
                             shell=True))
        time.sleep(1)


if __name__ == "__main__":
    main()
