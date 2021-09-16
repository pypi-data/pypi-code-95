# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-07-28 11:07:06
# @Last Modified by:   hhczy
# @Last Modified time: 2019-11-12 22:19:33
"""
    copy from scrapy
"""
import sys
import os
import optparse
import easyspider
from scrapy.cmdline import _run_command
from scrapy.cmdline import _run_print_help
from scrapy.cmdline import _pop_command_name
from scrapy.cmdline import _print_unknown_command
from scrapy.cmdline import _get_commands_from_module
from scrapy.cmdline import _get_commands_from_entry_points
# from scrapy.settings.deprecated import check_deprecated_settings
from scrapy.utils.project import inside_project, get_project_settings

# 目的就是替换掉这个，进而替换掉核心的引擎
# from scrapy.crawler import CrawlerProcess
try:
    from .easycrawler import easyCrawlerProcess
except:
    from easycrawler import easyCrawlerProcess

# 打印出来的提示信息也要变化


def _print_header(settings, inproject):
    if inproject:
        print("easyspider %s - project: %s\n" % (easyspider.__version__,
                                                 settings['BOT_NAME']))
    else:
        print("easyspider %s - no active project\n" % easyspider.__version__)


def _get_commands_dict(settings, inproject):
    cmds = _get_commands_from_module('easyspider.commands', inproject)
    cmds.update(_get_commands_from_entry_points(inproject))
    cmds_module = settings['COMMANDS_MODULE']
    if cmds_module:
        cmds.update(_get_commands_from_module(cmds_module, inproject))
    return cmds


def _print_commands(settings, inproject):
    _print_header(settings, inproject)
    print("Usage:")
    print("  easyspider <command> [options] [args]\n")
    print("Available commands:")
    cmds = _get_commands_dict(settings, inproject)
    for cmdname, cmdclass in sorted(cmds.items()):
        print("  %-13s %s" % (cmdname, cmdclass.short_desc()))
    if not inproject:
        print
        print("  [ more ]      More commands available when run from project directory")
    print
    print('Use "easyspider <command> -h" to see more info about a command')


def execute(argv=None, settings=None):
    if argv is None:
        argv = sys.argv

    # --- backwards compatibility for scrapy.conf.settings singleton ---
    if settings is None and 'scrapy.conf' in sys.modules:
        from scrapy import conf
        if hasattr(conf, 'settings'):
            settings = conf.settings
    # ------------------------------------------------------------------

    if settings is None:
        settings = get_project_settings()
        # set EDITOR from environment if available
        try:
            editor = os.environ.get('EDITOR') or None
        except Exception:
            pass
        else:
            settings['EDITOR'] = editor
    # check_deprecated_settings(settings)
    # ------------------------------------------------------------------

    inproject = inside_project()
    cmds = _get_commands_dict(settings, inproject)
    cmdname = _pop_command_name(argv)
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                   conflict_handler='resolve')
    if not cmdname:
        _print_commands(settings, inproject)
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(settings, cmdname, inproject)
        sys.exit(2)
    cmd = cmds[cmdname]
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    settings.setdict(cmd.default_settings, priority='command')
    cmd.settings = settings
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=argv[1:])
    _run_print_help(parser, cmd.process_options, args, opts)

    # 实际上只变更了这么一行
    # cmd.crawler_process = CrawlerProcess(settings)
    cmd.crawler_process = easyCrawlerProcess(settings)
    _run_print_help(parser, _run_command, cmd, args, opts)
    sys.exit(cmd.exitcode)


if __name__ == '__main__':
    execute()
