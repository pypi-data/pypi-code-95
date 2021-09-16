##
## this module is populated by casa_shell(...)
##
import os
import time
from casashell.private import userconfig

_tstamp = time.strftime("%Y%m%d-%H%M%S",time.gmtime())

##
## path to config directory
##
internal_configpath = os.path.realpath(os.path.join(os.path.dirname(__file__),'ttconfig'))

##
## paths added to the default casatools data path
##
datapath = userconfig.datapath if 'datapath' in dir(userconfig) else None
##
## path to log file
##
logfile = os.path.realpath(userconfig.logfile) if 'logfile' in dir(userconfig) else os.path.join(os.getcwd( ),'casa-'+_tstamp+'.log')
##
## path to ipython log file
##
iplogfile = os.path.realpath(userconfig.iplogfile) if 'iplogfile' in dir(userconfig) else os.path.join(os.getcwd( ),'ipython-'+_tstamp+'.log')
##
## directory containing casashell configuration files
##
rcdir = os.path.realpath(os.path.expanduser("~/.casa"))
##
## command line arguments
##
flags = None
##
## non-casashell arguments
##
args = None
