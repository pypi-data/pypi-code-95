import os
from time import sleep
from datetime import datetime
from termcolor import colored
from EventTimer.lib.Globals import color


def return_config_file(default_configs: list):
    argv_config = ""
    for default_config in default_configs:
        user_path = f"{os.path.expanduser('~')}{'/'}{default_config}"
        python_file_path = f"{os.path.realpath('')}{'/'}{default_config}"
        python_dir_path = f"{os.path.realpath('').split('/EventTimer')[0] + '/EventTimer'}{'/'}{default_config}"
        if os.path.exists(default_config):
            argv_config = default_config
            break
        elif os.path.exists(user_path):
            argv_config = user_path
            break
        elif os.path.exists(python_file_path):
            argv_config = python_file_path
            break
        elif os.path.exists(python_dir_path):
            argv_config = python_dir_path
            break
    sleep(1)
    os.system("clear")
    return argv_config


def print_from_seconds(gmt_second, edict):
    nepal_diff = seconds_from_time("05:45:00")
    india_diff = seconds_from_time("05:30:00")
    nepal = colored(time_from_seconds(gmt_second + nepal_diff), color="cyan")
    india = colored(time_from_seconds(gmt_second + india_diff), color="yellow")
    universal = colored(time_from_seconds(gmt_second), color="red")
    event_name = colored(edict["name"], color="green", attrs=["bold"])
    event_description = colored(edict["description"], color="white", attrs=["bold"])
    if event_description != "None":
        event_description = f"Description: {event_description}"
    else:
        event_description = ""

    print(f"{color.information} Event {event_name} | {color.other} {event_description}")
    print(
        f"{color.good} Universal/UTC Time: {universal}, Nepali Time: {nepal}, Indian Time: {india}\n"
    )
    return int(gmt_second - 1)


def print_banner():
    banner = "\x1b[1m\x1b[31m    ______                 __ _______                    \n   / ____/   _____  ____  / //_  __(_)___ ___  ___  _____\n  / __/ | | / / _ \\/ __ \\/ __// / / / __ `__ \\/ _ \\/ ___/\n / /___ | |/ /  __/ / / / /_ / / / / / / / / /  __/ /    \n/_____/ |___/\\___/_/ /_/\\__//_/ /_/_/ /_/ /_/\\___/_/     \n                                                         \n\n\x1b[0m"
    print(banner)


def seconds_from_time(time: str) -> int:
    if not time:
        return time
    time = time.split(":")
    hour, minute, second = int(time[0]), int(time[1]), int(time[2])
    return int(hour * 60 * 60) + int(minute * 60) + second


def time_from_seconds(second: int) -> str:
    if not second:
        return second
    minute, second = divmod(int(second), 60)
    hour, minute = divmod(int(minute), 60)
    return ":".join([str(hour).zfill(2), str(minute).zfill(2), str(second).zfill(2)])
