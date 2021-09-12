import os
from typing import Dict
from cnvrg.helpers.hash_helper import hash_file
import mimetypes
from pathlib import Path
from functools import reduce
def get_file_props(file: str, working_dir: str = None) -> Dict:
    '''

    :param file:
    :param working_dir:
    :return: {relative_path, file_name, file_size, content_type, sha1}
    '''
    working_dir = working_dir or ""
    abs_file_path = os.path.realpath(os.path.join(working_dir, file))
    relative_path = os.path.relpath(file, working_dir)
    size = os.path.getsize(abs_file_path)
    file_name = os.path.basename(abs_file_path)
    content_type = mimetypes.MimeTypes().guess_type(abs_file_path)[0] or "text/plain"
    return {
        "relative_path": relative_path,
        "file_name": file_name,
        "file_size": size,
        "content_type": content_type,
        "sha1": hash_file(abs_file_path, raw=True)
    }



def get_all_subpaths(*paths, ignores=[]):
    return reduce(lambda x,y: x+y, [expand(path, ignores) for path in paths])


def expand(path, ignores=[]):
    if not os.path.isdir(path): return [path]
    expanded_paths = []
    for p in Path(path).glob("**/*"):
        str_p = os.path.abspath(str(p))
        to_ignore = False
        for ignore in ignores:
            if ignore in str_p:
                to_ignore = True
                break
        if to_ignore: continue
        expanded_paths.append(str_p)

    return [os.path.relpath(exp_path, path) for exp_path in expanded_paths]