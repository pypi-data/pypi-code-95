import errno
import os
import json

try:
    from fcntl import flock, LOCK_EX, LOCK_UN
    from os import O_NONBLOCK
except:
    LOCK_EX = 0
    LOCK_UN = 1
    def fcntl(fd, op, arg=0):
        return 0
            
    def ioctl(fd, op, arg=0, mutable_flag=True):
        if mutable_flag:
            return 0
        else:
            return ""
        
    def flock(fd, op):
        return
            
    def lockf(fd, operation, length=0, start=0, whence=0):
        return

CONDA_MAGIC_FILE = 'conda.dependencies'


def get_conda_manifest_path(ds_root, flow_name):
    return os.path.join(ds_root, flow_name, CONDA_MAGIC_FILE)


def read_conda_manifest(ds_root, flow_name):
    path = get_conda_manifest_path(ds_root, flow_name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path) as f:
            return json.load(f)
    else:
        return {}


def write_to_conda_manifest(ds_root, flow_name, key, value):
    path = get_conda_manifest_path(ds_root, flow_name)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as x:
        if x.errno != errno.EEXIST:
            raise
    with os.fdopen(os.open(path, os.O_RDWR | os.O_CREAT), 'r+') as f:
        try:
            flock(f, LOCK_EX)
            data = {}
            if os.path.getsize(path) > 0:
                f.seek(0)
                data = json.load(f)
            data[key] = value
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        except IOError as e:
            if e.errno != errno.EAGAIN:
                raise
        finally:
            flock(f, LOCK_UN)