import os
import sys
from pathlib import Path
from clr_loader import get_coreclr
from pythonnet import set_runtime
import pkg_resources


runtime_config_file = pkg_resources.resource_filename(__name__, "AdSec_API.runtimeconfig.json")
sys.path.append(os.path.dirname(runtime_config_file))
rt = get_coreclr(runtime_config=runtime_config_file)
set_runtime(rt)
import clr  # Can't be imported until we've loaded the .NET Core runtime
clr.AddReference('AdSec_API')
clr.AddReference('AdSec_IO')
clr.AddReference('UnitsNet')
clr.AddReference('OasysUnits')
clr.AddReference('PythonNetHelpers')