import subprocess
import psutil
from cnvrg.helpers.logger_helper import log_message
import shlex
import threading
import re
import sys
import os
ON_POSIX = 'posix' in sys.builtin_module_names


def __send_cmd(cmd, cwd=None, env=None):
    is_windows = os.name == "nt"
    env = dict({**os.environ, **(env or {}), **{'PYTHONUNBUFFERED': "1"}})
    path = r"{exe} -u".format(exe=sys.executable)
    if is_windows:
        path = path.replace("\\", "\\\\")
    cmd = re.sub(r"^(python3?)", path, cmd)
    if not isinstance(cmd, list):
        cmd = shlex.split(cmd)
    params = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'close_fds': False,
        'bufsize': 1,
    }
    if cwd:
        params['cwd'] = r"{}".format(cwd)
    if env:
        params["env"] = env
    return subprocess.Popen(cmd, **params, shell=is_windows)


def __track_logs(buffer, output, print_output):
    for log in buffer:
        log = log.decode("utf-8")
        output.append(log)
        if print_output:
            log_message(log)

def run_sync(cmd, print_output=False, cwd=None, env=None, get_output_by_regex='.*'):
    proc = __send_cmd(cmd, cwd=cwd, env=env)
    output = []
    t1 = threading.Thread(target=__track_logs, args=(proc.stdout, output, print_output,))
    t2 = threading.Thread(target=__track_logs, args=(proc.stderr, output, print_output,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    proc.wait()
    return {"code": proc.returncode, "output": list(filter(re.compile(get_output_by_regex).search, output))}

def run_async(cmd):
    return __send_cmd(cmd)

def run_and_get_output(cmd):
    proc = __send_cmd(cmd)
    return "\n".join([line.decode("utf-8").strip() for line in proc.stdout])

def analyze_pid(proc=None, pid=None):
    if proc: pid = proc.pid
    if not pid: return
    p = psutil.Process(pid)
    with p.oneshot():
        return {"cpu": p.cpu_times(), "cpu_precent": psutil.cpu_percent(), "memory_info": psutil.virtual_memory(), "threads": p.num_threads(), "name": p.name()}