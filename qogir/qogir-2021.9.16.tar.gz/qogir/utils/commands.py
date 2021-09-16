from __future__ import absolute_import, print_function, unicode_literals
import subprocess
import sys


def run_bash_command(command):
    proc = subprocess.Popen(
        command,
        executable='/bin/bash',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    for line in iter(proc.stdout.readline, b''):
        print(line.strip().decode())

    proc.stdout.close()
    proc.wait()

    return proc.returncode
