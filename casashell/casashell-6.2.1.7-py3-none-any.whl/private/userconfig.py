from casashell import flags as _flags

if not _flags.norc:
    try:
        from casaconfig import *
    except:
        import os as _os
        if _flags.rcdir is None:
            _home = _os.curdir                        # Default
            if 'HOME' in _os.environ:
                _home = _os.environ['HOME']
            elif _os.name == 'posix':
                _home = _os.path.expanduser("~/")
            elif _os.name == 'nt':                   # Contributed by Jeff Bauer
                if 'HOMEPATH' in _os.environ:
                    if 'HOMEDRIVE' in _os.environ:
                        _home = _os.environ['HOMEDRIVE'] + _os.environ['HOMEPATH']
                    else:
                        _home = _os.environ['HOMEPATH']

            _config = _os.path.join(_home, ".casa/config.py")
        else:
            _config = _os.path.join(_os.path.expanduser(_flags.rcdir),"config.py")

        try:
            exec(open(_config).read( ))
            # let the user know where this config file that was just used was found
            # must be after the exec, here, so that the IOError exception is the only thing printed when that happens
            print("Using configuration file %s" % _config)
        except IOError:
            print("optional configuration file config.py not found, continuing CASA startup without it")
            pass
        except:
            import traceback
            traceback.print_exc( )
            print("evaluation of %s failed" % _config)
