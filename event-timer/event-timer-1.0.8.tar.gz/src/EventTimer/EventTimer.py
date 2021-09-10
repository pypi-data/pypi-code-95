#!/usr/bin/python3
import os
from time import sleep
from pytz import timezone
from argparse import ArgumentParser
from datetime import datetime
from dateutil.tz import tzlocal
from configparser import ConfigParser

from EventTimer.lib.Globals import pytz_map, default_config_files
from EventTimer.lib.Functions import return_config_file
from EventTimer.lib.Functions import print_banner, print_from_seconds


def parse_event_datetime(e: dict):
    gmt = timezone(pytz_map["GMT"])
    pst = timezone(pytz_map["PST"])
    pdt = timezone(pytz_map["PDT"])
    est = timezone(pytz_map["EST"])
    edt = timezone(pytz_map["EDT"])
    ktm = timezone(pytz_map["KTM"])
    cal = timezone(pytz_map["CAL"])

    event_date = e["date"]
    try:
        event_time = e["time"]
        event_tz = e["timeformat"]
    except KeyError:
        event_time = "00:00:00"
        event_tz = "None"
    event_datetime = datetime.strptime(
        f"{event_date} {event_time}", "%Y-%m-%d %H:%M:%S"
    )

    if event_tz == "GMT" or event_tz == "UTC":
        localized = gmt.localize(event_datetime, is_dst=None)
    elif event_tz == "PST":
        localized = pst.localize(event_datetime, is_dst=None)
    elif event_tz == "PDT":
        localized = pdt.localize(event_datetime, is_dst=None)
    elif event_tz == "EST":
        localized = est.localize(event_datetime, is_dst=None)
    elif event_tz == "EDT":
        localized = edt.localize(event_datetime, is_dst=None)
    elif event_tz == "KTM":
        localized = ktm.localize(event_datetime, is_dst=None)
    elif event_tz == "CAL":
        localized = cal.localize(event_datetime, is_dst=None)
    else:
        localized = gmt.localize(event_datetime, is_dst=None)
    return localized.astimezone(gmt)


def delta_seconds(e):
    current_datetime = datetime.now(tzlocal())
    event_datetime = parse_event_datetime(e)
    delta_datetime = event_datetime - current_datetime
    return int(delta_datetime.total_seconds())


def parse_config(config):
    parser = ConfigParser()
    parser.read(config)
    counters = []
    for event_item in parser.items():
        if event_item[0] != "DEFAULT":
            counter = delta_seconds(event_item[1])
            counters.append((counter, event_item[1]))
    return counters


def main():
    parser = ArgumentParser(description="\x1b[33mEventTimer\x1b[0m")
    parser.add_argument(
        "-b", "--banner", action="store_true", help="Print banner and exit"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Event Configs File (Common default is ~/.event.cfg)",
    )
    argv = parser.parse_args()

    if argv.banner:
        print_banner()
        exit()
    if not argv.config:
        argv.config = return_config_file(default_config_files)
        if not argv.config:
            print("Not found any configfile, use --help or README.md")
            exit()

    counters = parse_config(argv.config)
    try:
        while True:
            print("\x1b[%d;%dH" % (1, 1), end="")
            for i, c in enumerate(counters):
                counter, event_data = c[0], c[1]
                counter = print_from_seconds(counter, event_data)
                counters[i] = (counter, event_data)
            sleep(1)
    except KeyboardInterrupt:
        print("Exiting")
        exit()


if __name__ == "__main__":
    main()
