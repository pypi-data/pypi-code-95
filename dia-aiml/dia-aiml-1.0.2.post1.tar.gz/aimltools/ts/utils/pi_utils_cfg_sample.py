import sys
import clr

OSI_AFSDK_PATH = r'C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0'
OSI_PISDK_PATH = r'C:\Program Files\PIPC\pisdk\PublicAssemblies'
LLY_PIDRSDK_PATH = r'C:\Program Files\Eli Lilly\PIDataReaderApps'
MS_DOTNET_PATH = r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.6.2'

sys.path.append(OSI_AFSDK_PATH)
sys.path.append(OSI_PISDK_PATH)
sys.path.append(LLY_PIDRSDK_PATH)
sys.path.append(MS_DOTNET_PATH)

clr.AddReference('OSIsoft.AFSDK')
clr.AddReference('OSIsoft.PISDK')
clr.AddReference("System.Collections")
clr.AddReference('PIDataReaderLib')
clr.AddReference('mscorlib')

from OSIsoft.AF import *
from OSIsoft.AF.PI import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *
from OSIsoft.AF.UnitsOfMeasure import *
from System import *
from System.Collections.Generic import List
from System import DateTime, DateTimeOffset
from PIDataReaderLib import *