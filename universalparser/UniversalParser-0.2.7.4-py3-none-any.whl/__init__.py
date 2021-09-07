from ._parse import *
from ._ntype import *
from ._exception import *
from ._rely import *
from ._collections import *
from .manager import *
from .struct import *

# shotcut
from . import xml as XmlParser
from .html import odict as HtmlParser
from .micro import Excel as ExcelParser
from .micro import Word as WordParser
from .micro import PowerPoint as PowerPointParser

name = 'UniversalParser'
__version__ = '0.2.7.4'
__author__ = 'jiyang'
__license__ = 'MIT'
