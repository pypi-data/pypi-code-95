# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.clients.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Clients module initialization
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [ 'DirectClient', 'RestClient', 'CommandableHttpClient' ]

from .DirectClient import DirectClient
from .RestClient import RestClient
from .CommandableHttpClient import CommandableHttpClient
