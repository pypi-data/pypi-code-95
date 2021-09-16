from quickstats._version import __version__

import pathlib

import ROOT
ROOT.gROOT.SetBatch(True) 
ROOT.PyConfig.IgnoreCommandLineOptions = True
macro_path = pathlib.Path(__file__).parent.absolute()

MAX_WORKERS = 8

from quickstats.utils.io import VerbosePrint

_PRINT_ = VerbosePrint("INFO")

from quickstats.main import *

