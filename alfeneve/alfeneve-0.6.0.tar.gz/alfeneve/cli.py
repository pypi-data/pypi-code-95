# Copyright (c) 2019 Nick Douma <n.douma@nekoconeko.nl>
#
# This file is part of alfeneve .
#
# Licensed under the terms of the MIT license, see the
# LICENSE file in the root of the project.

from alfeneve.alfen import Alfen
from alfeneve.config import load_settings
from omniconf import config
from tabulate import tabulate
from tzlocal import get_localzone
import time


def categories_workflow(alfen):
    categories = alfen.categories()
    print(tabulate([{"category": c} for c in categories if c], headers="keys"))


def properties_workflow(alfen):
    props = alfen.properties(
        category=config("properties.category"),
        ids=config("properties.ids"))

    props = list(props)
    if len(props) == 0:
        print("No results")

    print(tabulate([p.to_dict(config("properties.verbose"))
                    for p in props], headers="keys"))


def whitelist_workflow(alfen):
    whitelist = alfen.whitelist(config("whitelist.index"))
    print(tabulate([w for w in whitelist if w], headers="keys"))


def transactions_workflow(alfen):
    for line in alfen.transactions():
        print(line)


def print_log(log):
    local = get_localzone()
    lid, timestamp, level, filename, linenum, line = log
    dt = timestamp.astimezone(local)
    dtf = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    print("{} {} {:4.4} {:20.20} {}"
          .format(lid, dtf, level, "{}:{}".format(filename, linenum),
                  line))


def logs_workflow(alfen):
    count = 0
    for line in alfen.logs(since=config("logs.since")):
        print_log(line)
        count += 1
        if count > config("logs.count"):
            break


def logs_follow_workflow(alfen):
    lastlog = config("logs.since")
    while True:
        count = 0
        logs = []
        for log in alfen.logs(since=lastlog):
            logs.append(log)
            count += 1
            if count > config("logs.count"):
                break
        for line in reversed(logs):
            print_log(line)
            lastlog = line[0]
        time.sleep(5)


def main():
    load_settings()
    with Alfen(endpoint=config("alfen.endpoint"),
               credentials=(config("alfen.username"),
                            config("alfen.password")),
               verify=config("alfen.certificate")) as alfen:
        if config("mode") == "properties":
            properties_workflow(alfen)
        elif config("mode") == "whitelist":
            whitelist_workflow(alfen)
        elif config("mode") == "transactions":
            transactions_workflow(alfen)
        elif config("mode") == "logs":
            if config("logs.follow"):
                try:
                    logs_follow_workflow(alfen)
                except KeyboardInterrupt:
                    pass
            else:
                logs_workflow(alfen)
        else:
            categories_workflow(alfen)


if __name__ == "__main__":  # pragma: nocover
    main()
