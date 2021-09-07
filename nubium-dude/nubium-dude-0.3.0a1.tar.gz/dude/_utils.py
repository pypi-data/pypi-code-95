import os
from pathlib import Path
import pty
import select
import subprocess
from typing import List

import click
from virtualenvapi.manage import VirtualEnvironment
from virtualenv import cli_run


def sync_virtual_environment():
    # TODO load virtualenv path from configuration
    venv_path = Path("venv")
    venv_path.mkdir(parents=True, exist_ok=True)
    # TODO load python version from configuration
    cli_run([str(venv_path), "-p", "python3.8"])
    venv = VirtualEnvironment(str(venv_path), readonly=True)
    if not venv.is_installed("pip-tools"):
        # TODO lock versions of pip-tools and dependencies
        run_command_in_virtual_environment(venv_path, "pip", args=["install", "pip-tools"])
    run_command_in_virtual_environment(venv_path, "pip-sync")


def run_command_in_virtual_environment(venv_path: Path, command: str, args: List[str] = None):
    if not args:
        args = []
    run_command_in_pseudo_tty(command=str(venv_path / "bin" / command), args=args)


def run_command_in_pseudo_tty(
    command: str,
    args: List[str] = None,
    output_handler=lambda data: click.echo(data, nl=False),
    buffer_limit=512,
    buffer_timeout_seconds=0.04,
):
    # In order to get colored output from a command, the process is unfortunately quite involved.
    # Constructing a pseudo terminal interface is necessary to fake most commands into thinking they are in an environment that supports colored output
    if not args:
        args = []

    # It's possible to handle stderr separately by adding p.stderr.fileno() to the rlist in select(), and setting stderr=subproccess.PIPE
    # which would enable directing stderr to click.echo(err=True)
    # probably not worth the additional headache
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen([command] + args, stdin=slave_fd, stdout=slave_fd, stderr=subprocess.STDOUT, close_fds=True)

    def is_proc_still_alive():
        return proc.poll() is not None

    while True:
        ready, _, _ = select.select([master_fd], [], [], buffer_timeout_seconds)
        if ready:
            data = os.read(master_fd, buffer_limit)
            output_handler(data)
        elif is_proc_still_alive():  # select timeout
            assert not select.select([master_fd], [], [], 0)[0]  # detect race condition
            break  # proc exited
    os.close(slave_fd)  # can't do it sooner: it leads to errno.EIO error
    os.close(master_fd)
    proc.wait()
