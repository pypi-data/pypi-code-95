# coding: utf-8
__version__ = "1.0.0b1"

"""
    refinitiv-data is a Python library to access Refinitiv Data Platform with Python.
"""

# do not remove this line --------------------------------------------------------------
from . import _data
from refinitiv.data._data.config_functions import get_config
from refinitiv.data._data.config_functions import load_config
from refinitiv.data._data.fin_coder_layer.session import open_session
from refinitiv.data._data.fin_coder_layer.session import close_session
from refinitiv.data._data.fin_coder_layer import get_data
from . import session
from . import delivery
from . import content
from . import errors
from . import eikon
from . import stream
