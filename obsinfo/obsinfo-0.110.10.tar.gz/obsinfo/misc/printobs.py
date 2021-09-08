#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions to print obsinfo objects

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA @UnusedWildImport

import os
from pathlib import Path, PurePath
import glob
import unittest
import inspect
import difflib
import re
import logging

#Third party
from obspy.core.utcdatetime import UTCDateTime
# from pprint import pprint
# import xml.etree.ElementTree as ET
# from CompareXMLTree import XmlTree
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)
from ..instrumentation import (Instrumentation, InstrumentComponent,
                                     Datalogger, Preamplifier, Sensor,
                                     ResponseStages, Stage, Filter)
from ..instrumentation.instrumentation import (Location)
from ..network import (Station, Network)
from ..instrumentation.filter import (Filter, PolesZeros, FIR, Coefficients, ResponseList,
                     Analog, Digital, AD_Conversion)


class PrintObs(object):
    """
    Collection of methods to print obsinfo objects at different levels of depth.
    All methods are static.
    
      **Attributes:**
     
        *None*
    
    """
    
    @staticmethod
    def print_component(obj, level="all"):
        """
        Prints comoponent information and continues if level is not "component" or "channel".
        
        If level is not "channel" detailed equipment information is not printed.
        
        :param level: determines to which level the *obsinfo* object will be printed
        
        """
        
        if not obj:
            return
        print(obj)
        if level == "channel":
            return 
        
        print(obj.equipment)
        
    @staticmethod
    def print_instrumentation(obj, level="all"):
        """
        Prints instrumentation information and continues if level is not "instrumentation".
        
        If level is  "response" or "all" response stages information will be printed (if it exists).
        Recall at this point all the response is gathered in ``instrument.response_stages.sgates``
        If level is "all" or "filter" (i.e. not "response") all information will be printed (only filter is left at this point...)
        
        :param level: determines to which level the *obsinfo* object will be printed
        
        """
        print(obj)
        print("Instrument:\n")
        print(obj.equipment)
        for k in obj.channels:
            print(k)
            if level != "instrumentation":
                print(k.instrument)
                PrintObs.print_component(k.instrument.sensor, level)
                PrintObs.print_component(k.instrument.preamplifier, level)
                PrintObs.print_component(k.instrument.datalogger, level)
                
                if level in  ["response", "all", "filter"] and k.instrument.response_stages:
                    for s in k.instrument.response_stages:
                       print(s)
                       if level in ["all", "filter"]:
                           print(s.filter) 
            
                
            
    
    @staticmethod            
    def print_station(obj, level="all"):
        """
        Prints station information and continues if level is not "station".
        
        :param level: determines to which level the *obsinfo* object will be printed
        """
        
        print(obj)
        print(obj.locations)
        for k, v in obj.locations.items():
            print(f'Location {k}: {v}')
        if level != "station":
            PrintObs.print_instrumentation(obj.instrumentation, level)
    
    @staticmethod        
    def print_network(obj, level="all"):
        """
        Prints network information and continues if level is not "network".
        
        :param level: determines to which level the *obsinfo* object will be printed
        """
        
        print(obj)
        print(obj.operator)
        if level != "network":
            for v in obj.stations:
                PrintObs.print_station(v, level)
                   
