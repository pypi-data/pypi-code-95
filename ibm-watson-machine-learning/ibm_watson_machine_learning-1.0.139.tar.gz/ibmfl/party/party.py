#!/usr/bin/env python3
import os
import sys
import importlib.util

import requests
import json

def process_heartbeat(kwargs):
    try:
        config_dict = kwargs.get('config_dict')
        agg_info = config_dict.get('aggregator')
        wml_services_url = agg_info["ip"].split("/")[0]

        hearbeat_resp = requests.get("https://" + wml_services_url + "/wml_services/training/heartbeat", verify=False)
        hearbeat_resp_json = json.loads(hearbeat_resp.content.decode("utf-8"))
        print(hearbeat_resp_json.get("service_implementation"))
        service_version = hearbeat_resp_json.get("service_implementation")

        if service_version.startswith("4.0"):
            return "cpd402"
        if service_version.startswith("353"):
            return "cpd35"

        return "cloud"

    except Exception as ex:
        print("unable to process heartbeat")
        return "cloud"



def import_source(module_file_path):
    module_name = 'ibmfl'
    
    module_spec = importlib.util.spec_from_file_location(
        module_name, module_file_path)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)


fl_path = os.path.abspath('.')
if fl_path not in sys.path:
    sys.path.append(fl_path)



class Party:
    """
    Party Wrapper for determining required version of FL Party to invoke.
    """

    SUPPORTED_PLATFORMS_MAP = {
        'cloud':"/cloud/ibmfl/__init__.py",
        'cpd35':"/cpd35/ibmfl/__init__.py",
        'cpd402':"/cpd402/ibmfl/__init__.py",
    } 

    def __init__(self, **kwargs):

        ibmfl_module = sys.modules['ibmfl'] 
        ibmfl_module_location_list = ibmfl_module.__path__
        
        # base location string, default to cloud location 
        ibmfl_module_location = ibmfl_module_location_list[0] 
        
        # get arg for platform
        calculated_platform_env = process_heartbeat(kwargs)
        platform_env = kwargs.get('env', calculated_platform_env)
        
        # process location 
        ibmfl_module_location = ibmfl_module_location + self.SUPPORTED_PLATFORMS_MAP.get(platform_env)
        
        del sys.modules['ibmfl']
        del sys.modules['ibmfl.party']
        del sys.modules['ibmfl.party.party']
        import_source(ibmfl_module_location )
        from ibmfl.party.party import Party
        self.Party = Party(**kwargs)
        self.connection = self.Party.connection

    def start(self):
        self.Party.start()

    def isStopped(self):
        return self.Party.connection.stopped