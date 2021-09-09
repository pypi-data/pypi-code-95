import hashlib
import os
import cnvrg.helpers.env_helper as env
import cnvrg.helpers.parallel_helper as parallel_helper
import cnvrg.helpers.cnvrgignore_helper as cnvrgignore_helper
from pathlib import Path
BUF_SIZE = 65536

def hash_dir(directory, pool_size=env.POOL_SIZE):
    files = list(map(str, Path(directory).rglob("*")))
    ignored = set(list(cnvrgignore_helper.get_full_ignore(directory)))
    files = set(files) - set(ignored)
    return dict(map(lambda x: [os.path.relpath(x[0], directory), x[1]], parallel_helper.safe_parallel(hash_file, filter(lambda x: not os.path.isdir(x), files), pool_size)))

def hash_file(file, raw=False):
    sha1 = hashlib.sha1()
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    if raw: return sha1.hexdigest()
    return str(file), {"sha1": sha1.hexdigest()}