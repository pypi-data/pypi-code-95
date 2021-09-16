###############################################################################
# Coscine Python Client
# Copyright (c) 2018-2021 RWTH Aachen University
# Contact: coscine@itc.rwth-aachen.de
# Git: https://git.rwth-aachen.de/coscine/docs/public/coscine-python-client
# Please direct bug reports, feature requests or questions at the URL above
# by opening an issue.
###############################################################################
# Coscine is an open source project at RWTH Aachen University for
# the management of research data.
# Visit https://coscine.de for more information.
###############################################################################

###############################################################################
# This file contains a command line printable banner. It is printed to stdout
# on initialization of a client with verbose mode enabled.
# The banner includes the current package version and author and otherwise
# serves no special purpose.
###############################################################################

from .about import __version__, __author__
import colorama

###############################################################################

BANNER = """%s%s
                     _             
                    (_)            
   ___ ___  ___  ___ _ _ __   ___  
  / __/ _ \/ __|/ __| | '_ \ / _ \ 
 | (_| (_) \__ \ (__| | | | |  __/ 
  \___\___/|___/\___|_|_| |_|\___| %s
____________________________________

    Coscine Python Client %s%s%s
    Copyright (c) 2019-2021
    %s
____________________________________%s
""" % (
  colorama.Back.BLACK,
  colorama.Fore.BLUE,
  colorama.Fore.WHITE,
  colorama.Fore.YELLOW,
	__version__,
  colorama.Fore.WHITE,
	__author__,
  colorama.Back.RESET
)

###############################################################################