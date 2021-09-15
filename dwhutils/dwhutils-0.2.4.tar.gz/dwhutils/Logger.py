import datetime
import logging
import os

from termcolor2 import colored

file_loggingPath = r"../logging"


def _log_to_cli(lg_str: str, lvl: str):
    if lvl == 'none':
        pass
    if lvl == 'info':
        logging.info(lg_str)
        print(colored(lg_str, 'green'))
    if lvl == 'warning':
        logging.info(lg_str)
        print(colored(lg_str, 'yellow'))
    if lvl == 'issue':
        logging.info(lg_str)
        print(colored(lg_str, 'red'))


def _log_to_file(lg_str: str, lvl: str, log_cls: str):
    if lvl == 'none':
        pass
    else:
        logging.info(lg_str)
        f = open(file=os.path.join(file_loggingPath, log_cls + ".log"), mode='a')
        f.write(lg_str)
        f.close()


def logger(logging_str: str = '', logging_class: str = '', log_to_cli: bool = True, log_to_file: bool = False,
           log_lvl: str = 'info'):
    now = datetime.datetime.now()
    log_str = "{d} : {c} : {l} : {s}".format(d=now, c=logging_class, l=log_lvl, s=logging_str)
    if log_to_cli:
        _log_to_cli(lg_str=log_str, lvl=log_lvl)
    if log_to_file:
        _log_to_file(lg_str=log_str, lvl=log_lvl,log_cls=logging_class)
