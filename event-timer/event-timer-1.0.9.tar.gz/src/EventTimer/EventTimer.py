#!/usr/bin/python3
import os
from time import sleep
from pytz import timezone
from argparse import ArgumentParser
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from dateutil.relativedelta import relativedelta
from configparser import ConfigParser

from EventTimer.lib.Globals import default_config_files
from EventTimer.lib.Globals import gmt, est, edt, pst, pdt, ktm, cal
from EventTimer.lib.Functions import return_config_file
from EventTimer.lib.Functions import print_banner, print_from_seconds


def parse_event_datetime(e: dict):
    event_date = e["date"]
    weekmodifiers = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6,
    }
    def weekday_to_number(weekday):
        if ' ' in weekday:
            weekday = weekday.split(' ')[-1]
        for weekmodifier in weekmodifiers:
            if weekmodifier in weekday.capitalize():
                weekday = weekmodifiers[weekmodifier]
                return weekday

    datemodifiers = {
        'daily': lambda d: datetime.now(), #+ timedelta(days=1),
        'weekly': lambda w: datetime.now() + relativedelta(weekday=weekday_to_number(w)),
        #'monthly': lambda m: datetime.now() + relativedelta(day=30)
    }
    for datemodifier in datemodifiers:
        if datemodifier in event_date:
            event_date = datemodifiers[datemodifier](event_date)
            event_date = event_date.strftime("%Y-%m-%d")
            break
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
        localized = event_datetime.astimezone(gmt)
        #localized = [localized, localized, localized.astimezone(ktm), localized.astimezone(cal)]
    elif event_tz == "PST":
        localized = event_datetime.astimezone(pst)
        #localized = [localized, localized.astimezone(gmt), localized.astimezone(ktm), localized.astimezone(cal)]
    elif event_tz == "PDT":
        localized = event_datetime.astimezone(pdt)
        #localized = [localized, localized.astimezone(gmt), localized.astimezone(ktm), localized.astimezone(cal)]
    elif event_tz == "EST":
        localized = event_datetime.astimezone(est)
        #localized = [localized, localized.astimezone(gmt), localized.astimezone(ktm), localized.astimezone(cal)]
    elif event_tz == "EDT":
        localized = event_datetime.astimezone(edt)
        #localized = [localized, localized.astimezone(gmt), localized.astimezone(ktm), localized.astimezone(cal)]
    elif event_tz == "KTM":
        localized = event_datetime.astimezone(ktm)
        #localized = [localized, localized.astimezone(gmt), localized, localized.astimezone(cal)]
    elif event_tz == "CAL":
        localized = event_datetime.astimezone(cal)
        #localized = [localized, localized.astimezone(gmt), localized.astimezone(ktm), localized]
    elif event_tz == "None":
        localized = event_datetime
        #localized = [localized, localized, localized, localized]
    return localized.astimezone(gmt)


def delta_seconds(e):
    current_datetime = datetime.now(tzlocal())
    event_datetime = parse_event_datetime(e)
    #all_datetimes = []
    #for event_datetime in event_datetimes:
    delta_datetime = event_datetime - current_datetime
    #all_datetimes.append(int(delta_datetime.total_seconds()))
    #return all_datetimes
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
