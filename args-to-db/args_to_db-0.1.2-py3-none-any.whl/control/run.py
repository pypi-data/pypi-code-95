import itertools
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from os import listdir
from os.path import isdir, isfile
from shutil import rmtree

import cursor
import pandas


class State(Enum):
    QUEUED = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3


class UIThread(threading.Thread):

    _frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    _update_interval = 0.2

    def __init__(self, states):
        super().__init__()
        self._frame_index = 0
        self._states = states
        self._states_lock = threading.Lock()
        self._stopevent = threading.Event()

    def update_state(self, cmd, state):
        with self._states_lock:
            self._states[cmd] = state

    def _print_states(self):

        for cmd, state in self._states.items():
            if state == State.QUEUED:
                icon = '⧖'
                color = None
            elif state == State.RUNNING:
                icon = self._frames[self._frame_index]
                color = None
            elif state == State.SUCCESS:
                icon = '✓'
                color = '\033[92m'
            elif state == State.FAILED:
                icon = '🗙'
                color = '\033[31m'
            else:
                raise Exception('Invalid ProcessState')

            out = color if color is not None else ''
            out += f'{icon} \033[0m {cmd} \n'
            sys.stdout.write(out)

    def run(self):
        cursor.hide()

        while not self._stopevent.is_set():
            self._frame_index = (self._frame_index + 1) % len(self._frames)
            self._print_states()

            sys.stdout.write(f'\033[{len(self._states)}A')
            sys.stdout.flush()

            time.sleep(self._update_interval)

        self._print_states()
        cursor.show()

    def join(self, timeout=None) -> None:
        self._stopevent.set()
        return super().join(timeout=timeout)


def run_shell_command(cmd, uithread):

    uithread.update_state(str(cmd), State.RUNNING)

    with subprocess.Popen(cmd.args(),
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL) as process:
        exit_code = process.wait()

    new_state = State.SUCCESS if exit_code == 0 else State.FAILED
    uithread.update_state(str(cmd), new_state)
    return exit_code


def _run_commands(command_list, threads):
    states = {str(cmd): State.QUEUED for cmd in command_list.commands()}
    uithread = UIThread(states)
    uithread.start()

    commands = command_list.commands()
    uithreads = itertools.repeat(uithread, len(commands))

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(run_shell_command, commands, uithreads)

    uithread.join()

    success = all((state == State.SUCCESS for state in states.values()))
    if not success:
        raise Exception('Command Failed!')


def _read_data_file(data_file):
    return pandas.read_pickle(data_file) if isfile(data_file) else None


def _combine_output_data(data_file, cache_dir):
    table = _read_data_file(data_file)

    for filename in listdir(cache_dir):

        row = pandas.read_pickle(f'{cache_dir}/{filename}')

        if table is None:
            table = row
        else:
            if row.iloc[0].name in table.index:
                table = table.update(row)
            else:
                table = table.append(row, verify_integrity=True)

    return table


def run(commands, threads=1, data_file='data.pkl', write_data=True,
        remove_cache_dir=True):
    cache_dir = 'args_to_db_cache'
    # assert isinstance(threads, int)
    # assert isinstance(data_file, str)
    # assert isinstance(write_data, bool)
    # assert isinstance(cache_dir, str)
    # assert isinstance(remove_cache_dir, bool)
    # assert isinstance(commands, (list, tuple))
    # for args in commands:
    #     assert isinstance(args, (list, tuple))
    #     for arg in args:
    #         assert isinstance(arg, str)

    _run_commands(commands, threads)

    if not isdir(cache_dir):
        return None

    table = _combine_output_data(data_file, cache_dir)

    if remove_cache_dir:
        rmtree(cache_dir)

    if write_data:
        table.to_pickle(data_file)
        table.to_csv(f'{data_file}.csv')

    return table
