from typing import Optional, Dict, List, Union
import enum

from quickstats.components import AnalysisObject
from quickstats.utils.common_utils import parse_config
from quickstats.utils.io import VerbosePrint

_PRINT_ = VerbosePrint("INFO")

class AsimovType(enum.Enum):
    S_NP_Nom               = -2
    B_NP_Nom               = -1
    B_NP_Fit               = 0
    S_NP_Fit               = 1
    S_NP_Fit_muhat         = 2
    B_unconstrained_NP_Fit = 3
    S_unconstrained_NP_Fit = 4
    S_unconstrained_NP_Fit_muhat = 5
    
class AsimovGenerator(AnalysisObject):

    ASIMOV_SETTINGS = {
        AsimovType.S_NP_Nom: {
            "asimov_name": "asimovData_0_NP_Nominal",
            "asimov_snapshot": "asimovData_0_NP_Nominal",
            "poi_val": 1,
            "poi_profile": 1,
            "do_fit": False,
            "modify_globs": False
        },
        AsimovType.B_NP_Nom: {
            "asimov_name": "asimovData_1_NP_Nominal",
            "asimov_snapshot": "asimovData_1_NP_Nominal",
            "poi_val": 0,
            "poi_profile": 0,
            "do_fit": False,
            "modify_globs": False
        },
        AsimovType.B_NP_Fit: {
            "asimov_name": "asimovData_0_NP_Profile",
            "asimov_snapshot": "asimovData_0_NP_Profile",
            "poi_val": 0,
            "poi_profile": 0,
            "do_fit": True,
            "modify_globs": True
        },
        AsimovType.S_NP_Fit: {
            "asimov_name": "asimovData_1_NP_Profile",
            "asimov_snapshot": "asimovData_1_NP_Profile",
            "poi_val": 1,
            "poi_profile": 1,
            "do_fit": True,
            "modify_globs": True
        },
        AsimovType.S_NP_Fit_muhat: {
            "asimov_name": "asimovData_muhat_NP_Profile",
            "asimov_snapshot": "asimovData_muhat_NP_Profile",
            "poi_val": 1,
            "poi_profile": None,
            "do_fit": True,
            "modify_globs": True
        },
        AsimovType.B_unconstrained_NP_Fit: {
            "asimov_name": "asimovData_0_unconstrained_NP_Profile",
            "asimov_snapshot": "asimovData_0_unconstrained_NP_Profile",
            "poi_val": 0,
            "poi_profile": 0,
            "do_fit": True,
            "modify_globs": True,
            "constraint_option": 1
        },
        AsimovType.S_unconstrained_NP_Fit: {
            "asimov_name": "asimovData_1_unconstrained_NP_Profile",
            "asimov_snapshot": "asimovData_1_unconstrained_NP_Profile",
            "poi_val": 1,
            "poi_profile": 1,
            "do_fit": True,
            "modify_globs": True,
            "constraint_option": 1
        },
        AsimovType.S_unconstrained_NP_Fit_muhat: {
            "asimov_name": "asimovData_muhat_unconstrained_NP_Profile",
            "asimov_snapshot": "asimovData_muhat_unconstrained_NP_Profile",
            "poi_val": 1,
            "poi_profile": None,
            "do_fit": True,
            "modify_globs": True,
            "constraint_option": 1
        }
    }    
    
    DEFAULT_ASIMOV_TYPES = [AsimovType.B_NP_Fit, AsimovType.S_NP_Fit, AsimovType.S_NP_Fit_muhat]
    
    def __init__(self, filename:str, poi_name:str=None, 
                 poi_scale:Optional[float]=None,
                 data_name:str='combData', 
                 config:Optional[Union[Dict, str]]=None,
                 verbosity:Optional[Union[int, str]]=None):
        
        config = parse_config(config)
        config['filename']  = filename
        config['data_name'] = data_name
        if verbosity is not None:
            _PRINT_.verbosity = verbosity
            config['verbosity'] = verbosity
        super().__init__(**config)
        
        if poi_name is None:
            poi = self.model.pois.first()
            if not poi:
                raise RuntimeError("No POI found in the workspace")
            _PRINT_.info(f"INFO: POI not specified. The first POI `{poi.GetName()}` will be used.")
            
        self.poi_name = poi_name
        self.poi_scale = poi_scale
        
    
    def generate(self, asimov_types:Optional[Union[List[AsimovType], List[int]]]=None):
        if asimov_types is None:
            asimov_types = self.DEFAULT_ASIMOV_TYPES
        for asimov_type in asimov_types:
            if isinstance(asimov_type, int):
                asimov_type = AsimovType(asimov_type)
            kwargs = self.ASIMOV_SETTINGS[asimov_type]
            kwargs['poi_name'] = self.poi_name
            for key in ['poi_val', 'poi_profile']:
                if kwargs[key] is not None:
                    kwargs[key] *= self.poi_scale
            kwargs['minimizer_options'] = self.minimizer_options
            kwargs['nll_options'] = self.nll_commands
            self.model.generate_asimov(**kwargs)
            
    def save(self, fname:str, recreate:bool=True):
        self.model.save(fname, recreate=recreate)
        _PRINT_.info(f"INFO: Saved workspace file as `{fname}`")