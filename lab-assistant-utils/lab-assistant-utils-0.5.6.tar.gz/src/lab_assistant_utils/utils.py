import os
import sys
from typing import Dict


def expand_variables(content: str, replace_vars: Dict[str, str]):
    for k, v in replace_vars.items():
        content = content.replace('$' + k, v)
        content = content.replace('${' + k + '}', v)
    return content


def parse_image_name(image_name: str):
    if '/' in image_name:
        image_name_parts = image_name.split('/')
        registry_name = image_name_parts[0]
        root_image_name = image_name_parts[1].split(':')[0]
    else:
        registry_name = None
        root_image_name = image_name.split(':')[0]
    image_version = image_name.split(':')[1]
    return registry_name, root_image_name, image_version


def fork_and_wait():
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        # Child process
        os.dup2(r, sys.stdin.fileno())
        os.close(r)
        os.close(w)
        up_command = 'docker-compose -f - up --build --force-recreate'.split()
        os.execvp(up_command[0], up_command)
    else:
        # Parent process
        os.close(r)
        os.write(w, bytearray(prepared_config, 'utf-8'))
        os.close(w)  # When done writing
        pid, status = os.waitpid(pid, 0)