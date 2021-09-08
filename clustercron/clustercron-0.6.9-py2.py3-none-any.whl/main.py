# clustercron/clustercron.py
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# -*- coding: utf-8 -*-

'''
clustercron.main
----------------------
'''


from __future__ import print_function, unicode_literals

import logging
import os
import os.path
import stat
import subprocess
import sys

from . import __version__, cache, config

# general libary logging
logger = logging.getLogger(__name__)


def clustercron(lb_type, name, command, output, use_cache):
    '''
    API clustercron

    :param lb_type: Type of loadbalancer
    :param name: Name of the loadbalancer instance
    :param command: Command as a list
    :param output: Boolean
    '''
    if lb_type == 'elb':
        from . import elb

        lb = elb.Elb(name)
    elif lb_type == 'alb':
        from . import alb

        lb = alb.Alb(name)
    else:
        lb = None
    if lb is not None:
        if use_cache:
            master = cache.check(lb.master, **config.cache)
        else:
            master = lb.master()
        if master:
            if command:
                logger.info('run command: %s', ' '.join(command))
                try:
                    proc = subprocess.Popen(
                        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    stdout, stderr = proc.communicate()
                    return_code = proc.returncode
                except OSError as error:
                    stdout = None
                    stderr = str(error)
                    return_code = 2
                if output:
                    if stdout:
                        print(stdout.strip(), file=sys.stdout)
                    if stderr:
                        print(stderr.strip(), file=sys.stderr)
                logger.info('stdout: %s', stdout)
                logger.info('stderr: %s', stderr)
                logger.info('returncode: %d', return_code)
                return return_code
            else:
                return 0
        else:
            return 1


class Optarg(object):
    '''
    Parse arguments from `sys.argv[0]` list.
    Set usage string.
    Set properties from arguments.
    '''

    def __init__(self, arg_list):
        self.arg_list = arg_list
        self.args = {
            'version': False,
            'help': False,
            'output': False,
            'verbose': 0,
            'syslog': False,
            'cache': False,
            'lb_type': None,
            'name': None,
            'command': [],
        }
        self.usage = '''Clustercron, cluster cronjob wrapper.

Usage:
    clustercron [options] elb <loadbalancer_name> [<cron_command>]
    clustercron [options] alb <target_group_name> [<cron_command>]
    clustercron -h | --help
    clustercron --version

Options:
    -v --verbose  Info logging. Add extra `-v` for debug logging.
    -s --syslog   Log to (local) syslog.
    -c --cache    Cache output from master check.
    -o --output   Output stdout and stderr from <cron_command>.

Clustercron is cronjob wrapper that tries to ensure that a script gets run
only once, on one host from a pool of nodes of a specified loadbalancer.

Without specifying a <cron_command> clustercron will only check if the node
is the `master` in the cluster and will return 0 if so.
'''

    def parse(self):
        arg_list = list(self.arg_list)
        arg_list.reverse()
        while arg_list:
            arg = arg_list.pop()
            if arg == '-h' or arg == '--help':
                self.args['help'] = True
                break
            if arg == '--version':
                self.args['version'] = True
                break
            if arg in ('-v', '--verbose'):
                self.args['verbose'] += 1
            if arg in ('-o', '--output'):
                self.args['output'] = True
            if arg in ('-s', '--syslog'):
                self.args['syslog'] = True
            if arg in ('-c', '--cache'):
                self.args['cache'] = True
            if arg in ('elb', 'alb'):
                self.args['lb_type'] = arg
                try:
                    self.args['name'] = arg_list.pop()
                except IndexError:
                    pass
                arg_list.reverse()
                self.args['command'] = list(arg_list)
                break
        if self.args['name'] and self.args['name'].startswith('-'):
            self.args['name'] = None
        if self.args['command'] and self.args['command'][0].startswith('-'):
            self.args['command'] = []
        logger.debug('verbose: %s', self.args['verbose'])


def setup_logging(verbose, syslog):
    '''
    Sets up logging.
    '''
    logger = logging.getLogger()
    # Make sure no handlers hangin' round
    [handler.close() for handler in logger.handlers]
    logger.handlers = []
    # root logger logs all
    logger.setLevel(logging.DEBUG)
    # Get log level for handlers
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.ERROR
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(levelname)-8s %(name)s : %(message)s')
    if syslog:
        unix_socket = {
            'linux2': os.path.realpath('/dev/log'),
            'darwin': os.path.realpath('/var/run/syslog'),
        }.get(sys.platform, '')
        if os.path.exists(unix_socket) and stat.S_ISSOCK(
            os.stat(unix_socket).st_mode
        ):
            handler = logging.handlers.SysLogHandler(unix_socket)
            formatter = logging.Formatter(
                fmt='%(name)s [%(process)d]: %(message)s', datefmt=None
            )
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)


def command():
    '''
    Entry point for the package, as defined in setup.py.
    '''
    optarg = Optarg(sys.argv[1:])
    optarg.parse()
    if optarg.args['version']:
        print(__version__)
        exitcode = 2
    elif optarg.args['lb_type'] and optarg.args['name']:
        setup_logging(optarg.args['verbose'], optarg.args['syslog'])
        logger.debug('Command line arguments: %s', optarg.args)
        exitcode = clustercron(
            optarg.args['lb_type'],
            optarg.args['name'],
            optarg.args['command'],
            optarg.args['output'],
            optarg.args['cache'],
        )
    else:
        print(optarg.usage)
        exitcode = 3
    return exitcode
