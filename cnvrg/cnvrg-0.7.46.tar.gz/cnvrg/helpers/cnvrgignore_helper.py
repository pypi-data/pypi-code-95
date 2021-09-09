import os
import re
from pathlib import Path
def ignore_path(path):
    return os.path.join(path,'.cnvrgignore')

def generate_cnvrgignore(path):
    content = """# cnvrg ignore: Ignore the following directories and files
    # for example:
    # some_dir/
    # some_file.txt
    .git/*
    .cnvrg/*
    .gitignore
    *.conflict
    *.deleted"""
    with open(ignore_path(path), 'w') as f:
        f.write(content)

def check_cnvrgignore(path):
    if not os.path.exists(ignore_path(path)):
        generate_cnvrgignore(path)

def blank_ignores(f):
    return not f.startswith("#")

def remove_blanks(f):
    return re.sub("\s", "", f)

def read_cnvrgignore(path):
    i_path = ignore_path(path)
    if not os.path.exists(i_path): return []
    with open(i_path, 'r') as f:
        return (filter(blank_ignores, map(remove_blanks, f.readlines())))

def get_full_ignore(path):
    ignores = []
    for ignore in (list(read_cnvrgignore(path)) + [".cnvrg/*"]):
        if ignore.endswith("/"): ignore = ignore + "**/*"
        elif os.path.isdir(ignore): ignore = ignore + "/**/*"
        elif not ignore: continue
        files = list(Path(path).glob(ignore))
        ignores.extend(files)
    return list(map(lambda x: str(x), ignores))
