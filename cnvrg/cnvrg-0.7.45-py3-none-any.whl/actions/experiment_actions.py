from cnvrg.modules.experiment import Experiment
from cnvrg.modules.experiment import LOGS_TYPE_OUTPUT, LOGS_TYPE_ERROR
import cnvrg.helpers.spawn_helper as spawn_helper
from cnvrg.libs.limit import limit
import queue
import dill
import time
from threading import Thread
import multiprocessing
import io


STOP_MESSAGE = "@AFSDFAQ#$TASDFQ@#$RKASDLFAKSDLFM<AQL@#$MTLAS<DLF<AWLMNOQ#K$%LAW<EFL:A<>D:ALS:FW$<TRLEMFLAMSDFAsf"
SLEEP_DELAY = 0.001


def __logging_thread(experiment, pid, error_log=False):
    log_type = LOGS_TYPE_ERROR if error_log else LOGS_TYPE_OUTPUT
    q = multiprocessing.Manager().Queue()
    fid = pid.stderr if error_log else pid.stdout
    t = Thread(target=log_exp, args=(experiment, q, log_type))
    t.start()
    time.sleep(1)
    print("start")
    for line in iter(fid.readline, b''):
        print(line.rstrip())
        q.put(line.decode("utf-8").rstrip())
    print("IM HERE!!")
    fid.close()
    q.put(STOP_MESSAGE)
    t.join()

def __monitoring_thread(experiment, pid):
    ### check every second if the process died, send utilization every 15 seconds.
    while pid.poll() != None:
        for i in range(30):
            time.sleep(1)
            if pid.poll() != None:
                return
        monitor(experiment, pid)

def monitor(experiment, pid):
    if pid.poll() != None:
        return
    utilization = spawn_helper.analyze_pid(pid)
    experiment.send_util(utilization)

def log_exp(experiment: Experiment, q: queue.Queue, log_type="output"):
    while True:
        if q.empty():
            print("Q is empty")
            time.sleep(0.5)
            continue
        logs = []
        while not q.empty():
            logs.append(q.get())
        print(logs)
        experiment.log(list(filter(lambda x: x is not STOP_MESSAGE, logs)), log_type=log_type)
        if STOP_MESSAGE in logs:
            return
        time.sleep(3)

def exec(exp_slug):
    experiment = Experiment(exp_slug)
    cmd = experiment["input"]
    pid = spawn_helper.__send_cmd(cmd, env={"CNVRG_JOB_ID": exp_slug, "CNVRG_JOB_TYPE": "Experiment"})
    logger = Thread(target=__logging_thread, args=(experiment, pid, False))
    logger.start()
    utilization = Thread(target=__monitoring_thread, args=(experiment, pid))
    utilization.start()
    while pid.poll() == None:
        time.sleep(0.5)
    utilization.join()
    logger.join()

    experiment.finish(exit_status=pid.poll())

def exec_pickle(file, **kwargs):
    with open(file, 'rb') as f:
        func = dill.load(f)
        Experiment.run(func, **kwargs)



