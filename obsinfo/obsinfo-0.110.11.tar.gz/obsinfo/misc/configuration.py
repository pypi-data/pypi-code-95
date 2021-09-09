import os
import sys
import re
from pathlib import Path
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import yaml
import logging
logger = logging.getLogger("obsinfo")


class Singleton:
    """
    Class to implement singleton pattern design in Python
    """

    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        msg = 'Singletons must be accessed through `Instance()`.'
        logger.debug("Programming error: " + msg)
        raise AttributeError(msg)

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)
    
 
@Singleton
class ObsinfoConfiguration:
    """
    Singleton class to store obsinfo configuration, basically its directories to store files
    and its version
    
      **Attributes:**
     
    
        * obsinfo_datapath: list of strings representing directories to search for info files 
        * gitlab_repository (str): remote Gitlab repository name
        * gitlab_project (str): project within the repository
        * gitlab_path (str): path to info files within the project
        * obsinfo_version (str): version of this program
      
    """
    
    logger = None
        
    def __init__(self):
        """
        Read .obsinforc file in home directory and setup the configuration
        :raises: FileNotFoundError, OSError
        """
        
        home = Path.home()
        config_file = Path(home).joinpath(".obsinforc")
        # This is called directly to avoid the paraphernalia of yamlref.
        try:
            with open(config_file, "r") as fp:
               config_dict = yaml.safe_load(fp)
        except FileNotFoundError:
            msg = "Configuration file .obsinforc not found. Run obsinfo-setup"
            print(msg)
            logger.error(msg)
            raise
        except OSError:
            msg = "Operating system error reading configuration file .obsinforc"
            print(msg)
            logger.error(msg)
            raise 
        
        self.obsinfo_datapath = config_dict.get("datapath", "")
        self.gitlab_repository = config_dict.get("gitlab_repository", "")
        self.gitlab_project = config_dict.get("gitlab_project", "")
        self.gitlab_path = config_dict.get("gitlab_path", "")
        self.obsinfo_branch = str(config_dict.get("obsinfo_branch", ""))
        
    
           

