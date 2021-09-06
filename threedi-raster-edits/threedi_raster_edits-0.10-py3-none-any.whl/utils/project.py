# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:56:20 2019

@author: chris.kerklaan - N&S
"""
# First-party imports
import os
import sys
import json
import logging
import datetime
import shutil
import tempfile

# Globals
time_last_print_small = datetime.datetime.now()
time_last_print_large = datetime.datetime.now()


def log_time(log_type, s1="", s2="", size="s"):
    print_time(s1=s1, s2=s2, size=size)

    if log_type == "info":
        logging.info("%s - %s", s1, s2)
    elif log_type == "debug":
        logging.debug("%s - %s", s1, s2)
    elif log_type == "warning":
        logging.warning("%s - %s", s1, s2)
    elif log_type == "error":
        logging.error("%s - %s", s1, s2)
    else:
        print("no log")


class Logger(object):
    def __init__(self, path, quiet=False):
        # self.terminal = sys.stdout
        self.log = open(path, "a")
        self.quiet = quiet
        self.path = path

    def set_subject(self, subject):
        self.s1 = subject

    def show(self, s2="", quiet=None, size="s"):
        # if self.quiet or quiet:
        #     be_quiet=True
        # else:
        #     be_quiet=False

        # if not be_quiet:
        global time_last_print_small
        global time_last_print_large

        now = datetime.datetime.now()
        if size == "s":
            _print = "{} - {} - {} - {}".format(
                now, now - time_last_print_small, self.s1, s2
            )

        elif size == "l":
            _print = "{} - {} - {} - {}".format(
                now, now - time_last_print_large, self.s1, s2
            )

        else:
            pass

        time_last_print_small = now
        time_last_print_large = now

        print(_print + "\n")
        self.log.write(_print + "\n")

    def close(self):
        self.log = None

    def write(self):
        self.log = None
        self.log = open(self.path, "a")


def print_time(s1="", s2="", size="s", quiet=False):
    if not quiet:
        global time_last_print_small
        global time_last_print_large

        now = datetime.datetime.now()
        if size == "s":
            _print = "{} - {} - {} - {}".format(
                now, now - time_last_print_small, s1, s2
            )

        elif size == "l":
            _print = "{} - {} - {} - {}".format(
                now, now - time_last_print_large, s1, s2
            )

        else:
            pass

        time_last_print_small = now
        time_last_print_large = now
        return print(_print + "\n")


def percentage(count, total):
    return str((count / total) * 100) + "%"


def mk_temp(path=os.getcwd()):
    tempfolder = os.path.join(path, "temp")
    if not os.path.exists(tempfolder):
        os.mkdir(tempfolder)
    return tempfolder


def print_list(_list, subject):
    if not isinstance(_list, list):
        _list = [_list]

    print("\n {}:".format(subject))
    for path in _list:
        print("\t{}".format(str(path)))


def print_dictionary(_dict, subject):
    print("\n {}:".format(subject))
    for key, value in _dict.items():
        print("\t{}:\t\t{}".format(str(key), str(value)))


def write_dictionary(path, _dict):
    with open(path, "w") as write_file:
        json.dump(_dict, write_file, indent=4)


def load_dictionary(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def mk_dir(path=os.getcwd(), folder_name="temp", overwrite=True):
    tempfolder = os.path.join(path, folder_name)

    if os.path.exists(tempfolder) and overwrite:
        shutil.rmtree(tempfolder)
        os.mkdir(tempfolder)
    elif not os.path.exists(tempfolder):
        os.mkdir(tempfolder)
    else:
        pass  # Folder exits, path
    return tempfolder


def create_temporary_copy(path):
    temp = tempfile.NamedTemporaryFile("w+t", delete=True)
    shutil.copy2(temp.name, path)
    return temp.name


class Progress:
    def __init__(self, total, message, size=30, file=sys.stdout):
        self.total = total
        self.message = message
        self.size = size
        self.file = file
        self.i = 0
        self.time = datetime.datetime.now()

    def update(self, quiet=False):
        if quiet:
            return

        self.i += 1
        x = int(self.size * self.i / self.total)

        print(
            f"\r{self.message}: [{'.'*x}{' '*(self.size-x)}] {self.i}/{self.total}",
            end="\r",
            flush=True,
        )

        if self.i >= self.total:
            end_time = datetime.datetime.now() - self.time
            print(
                f"\r{self.message}: Completed {self.total} loops in {end_time}",
                end="\r",
                flush=True,
            )
