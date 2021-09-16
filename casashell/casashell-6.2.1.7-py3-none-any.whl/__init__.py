import os as _os
import sys as _sys
import argparse as _argparse
from traitlets.config.loader import Config

__name__ = 'casashell'
__all__ = [ "start_casa", "argv", "flags", "version", "version_string", "extra_task_modules" ]

extra_task_modules = [ ]

def version( ): return [ 6, 2, 1,7 ]
def version_string( ): return "6.2.1.7"

argv = _sys.argv

flags = [ ]

def __init_config(config,flags,args):
    if flags.datapath is not None:
        datap = list(map(_os.path.abspath,filter(_os.path.isdir,list(flags.datapath.split(':')))))
        config.datapath = datap
    if flags.logfile is not None:
        config.logfile = flags.logfile if flags.logfile.startswith("/") else _os.path.realpath(_os.path.join('.',flags.logfile))

    config.flags = flags
    config.args = args
                
def start_casa( argv ):
    moduledir = _os.path.dirname(_os.path.realpath(__file__))

    ###
    ### this will be used by inp/go which are introduced in init_subparam
    ###
    casa_inp_go_state = { 'last': None }

    ###
    ### this will be used by register_builtin for making casa builtins immutable
    ###
    casa_builtin_state = { }
    casa_nonbuiltin_state = { }    ### things that should be builtin but are not

    ##
    ## this is filled via add_shutdown_hook (from casa_shutdown.py)
    ##
    casa_shutdown_handlers = [ ]

    ##
    ## filled when -c <args> is used
    ##
    casa_eval_status = { 'code': 0, 'desc': 0 }

    init_scripts = [ "init_begin_startup.py",
                     "init_system.py",
                     "load_tasks.py",
                     "load_tools.py",
                     "init_subparam.py",
                     "init_doc.py",
    ]
    # optional user startup.py and init_welcome.py added later - after optional init_pipeline.py

    ##
    ## final interactive exit status...
    ## runs using "-c ..." exit from init_welcome.py
    ##
    _exit_status=0
    try:
        parse = _argparse.ArgumentParser(prog="casa",description='CASA bootstrap')
        parse.add_argument( '--logfile',dest='logfile',default=None,help='path to log file' )
        parse.add_argument( "--log2term",dest='log2term',action='store_const',const=True,default=False,
                            help='direct output to terminal' )
        parse.add_argument( "--nologger",dest='nologger',action='store_const',const=True,default=False,
                            help='do not start CASA logger' )
        parse.add_argument( "--nologfile",dest='nologfile',action='store_const',const=True,default=False,
                            help='do not create a log file' )
        parse.add_argument( "--nogui",dest='nogui',action='store_const',const=True,default=False,
                            help='avoid starting GUI tools' )
        parse.add_argument( "--rcdir",dest='rcdir',default=None,
                            help='location for startup files')
        parse.add_argument( "--norc",dest='norc',action='store_const',const=True,default=False,
                            help='do not load user config.py' )
        parse.add_argument( '--colors', dest='prompt', default='Neutral',
                            help='prompt color', choices=['Neutral', 'NoColor', 'Linux', 'LightBG'] )
        parse.add_argument( "--pipeline",dest='pipeline',action='store_const',const=True,default=False,
                            help='start CASA pipeline run' )
        parse.add_argument( "--agg",dest='agg',action='store_const',const=True,default=False,
                            help='startup without graphical backend' )
        parse.add_argument( '--iplog',dest='ipython_log',default=False,
                            const=True,action='store_const',
                            help='create ipython log' )
        parse.add_argument( '--notelemetry',dest='notelemetry',default=False,
                            const=True,action='store_const',
                            help='disable telemetry collection')
        parse.add_argument( '--nocrashreport',dest='nocrashreport',default=False,
                            const=True,action='store_const',
                            help='do not submit an online report when CASA crashes')
        parse.add_argument( '--datapath',dest='datapath',default=None,
                            help='data path(s) [colon separated]' )
        parse.add_argument( "--user-site",dest='user_site',default=False,
                            const=True,action='store_const',
                            help="include user's local site-packages lib in path" )
        parse.add_argument( "-c",dest='execute',default=[],nargs=_argparse.REMAINDER,
                            help='python eval string or python script to execute' )

        # obsolete arguments still parsed here so that they now generate errors when invoked
        # help is suppressed to hide them in the usage output

        # was help='list imported modules'
        parse.add_argument( "--trace",dest='trace',action='store_const',const=True,default=False,
                            help=_argparse.SUPPRESS)
        
        # telemetry collection is now enabled by default, added notelemetry to toggle it off here
        # was help='Enable telemetry collection'
        parse.add_argument( '--telemetry',dest='telemetry',default=False,
                            const=True,action='store_const',
                            help=_argparse.SUPPRESS)

        # this was silently turned off several releases ago. It used to use "console" on macs due to perceived slowness of casalogger
        # was help='logger to use on Apply systems'
        parse.add_argument( "--maclogger",dest='maclogger',action='store_const',const='console',
                            default='/does/this/still/make/sense',
                            help=_argparse.SUPPRESS )
        
        flags,args = parse.parse_known_args(argv)

        # watch for the discontinued arguments, just warn
        if flags.trace:
            print("\nWARN: --trace is not available.\n")

        if flags.telemetry:
            print("\nERROR: --telemetry is unsupported.\n")
            print("Telemetry is enabled by default. It can be disabled through the --notelemetry option or by adding the following to your ~/.casa/config.py:\n")
            print("telemetry_enabled = False\n")

        if flags.maclogger=='console':
            print("\nWARN: --maclogger is not available. The default casalogger will be used.\n")

        # having the current working directory (an empty element) in sys.path can cause problems - protect the user here
        _sys.path = [p for p in _sys.path if len(p) > 0]
        # if user installs casatools into their local site
        # packages it can cause problems
        if not flags.user_site:
            if _sys.platform == "darwin":
                _sys.path = [p for p in _sys.path if _os.path.join(_os.path.expanduser("~"),"Library/Python",) not in p]
            else:
                _sys.path = [p for p in _sys.path if _os.path.join(_os.path.expanduser("~"),".local","lib",) not in p]

            _os.environ['PYTHONNOUSERSITE'] = "1"
        else:
            # this makes no sense if PYTHONOOUSERSITE is already set
            if 'PYTHONNOUSERSITE' in _os.environ:
                print("\nERROR: --user-site has been used while PYTHONNOUSERSITE is set. Please unset PYTHONNOUSERSITE and try --user-site again.\n")
                _sys.exit(1)

        # nogui implies nologger
        if flags.nogui:
            flags.nologger = True

        # nologfile implies --logfile /dev/null
        # also nologfile takes precedence over logfile argument
        if flags.nologfile:
            flags.logfile = "/dev/null"

        import casashell as _cs
        _cs.argv = argv
        _cs.flags = flags

        # import of this config deferred to here so that _cs flags is set and available for use
        # by scripts imported by this step
        from .private import config        
        casa_config_master = config
        __init_config(casa_config_master,flags,args)

        from IPython import __version__ as ipython_version
        configs = Config( )
        if flags.rcdir is not None:
            config.rcdir = _os.path.expanduser(flags.rcdir)
            ### casatools looks in casashell._rcdir (if it's
            ### available) for a distro data repository
            _cs._rcdir = _os.path.expanduser(flags.rcdir)

        if flags.pipeline:
            init_scripts += [ "init_pipeline.py" ]

        if _os.path.isfile(_os.path.abspath(_os.path.join(config.rcdir,"startup.py"))):
            # let the user know where startup.py is coming from
            startupPath = _os.path.abspath(_os.path.join(config.rcdir,"startup.py"))
            print("Using user-supplied startup.py at %s" % startupPath)
            init_scripts += [ startupPath ]

        init_scripts += [ "init_welcome.py" ]
        startup_scripts = filter( _os.path.isfile, map(lambda f: _os.path.join(moduledir,"private",f), init_scripts ) )

        configs.TerminalInteractiveShell.ipython_dir = _os.path.join(config.rcdir,"ipython")
        configs.TerminalInteractiveShell.banner1 = 'IPython %s -- An enhanced Interactive Python.\n\n' % ipython_version
        configs.TerminalInteractiveShell.banner2 = ''
        configs.HistoryManager.hist_file = _os.path.join(configs.TerminalInteractiveShell.ipython_dir,"history.sqlite")
        configs.TerminalIPythonApp.matplotlib = 'agg' if flags.agg or flags.pipeline else 'auto'
        configs.InteractiveShellApp.exec_files = list(startup_scripts)

        _os.makedirs(_os.path.join(config.rcdir,"ipython"),exist_ok=True)
        from IPython import start_ipython
        start_ipython( config=configs, argv= (['--logfile='+config.iplogfile] if flags.ipython_log else []) + ['--ipython-dir='+_os.path.join(config.rcdir,"ipython"), '--autocall=2', '--colors='+flags.prompt] + (["-i"] if len(flags.execute) == 0 else ["-c","__evprop__(%s)" % flags.execute]) )

    except:
        casa_eval_status['code'] = 1
        casa_eval_status['desc'] = "unexpected error"
        pass

    ### this should (perhaps) be placed in an 'atexit' hook...
    for handler in casa_shutdown_handlers:
        handler( )

    #from init_welcome_helpers import immediate_exit_with_handlers
    #immediate_exit_with_handlers(_exit_status)
    return casa_eval_status['code']
