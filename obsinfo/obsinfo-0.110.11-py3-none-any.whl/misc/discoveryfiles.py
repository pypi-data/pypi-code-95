import sys
import os
import re
from pathlib import Path
from urllib import parse as urlparse
from urllib.parse import urljoin 
import warnings
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
import yaml
import logging
logger = logging.getLogger("obsinfo")

# obsinfo modules
from ..misc.remoteGitLab import gitLabFile
from .configuration import ObsinfoConfiguration

# We'll first create all the various objects. These strongly follow the
# hierarchy of StationXML files.


class Datapath(object):
    """
    Class to discover where information files are stored.
    
      **Attributes:**
     
    
         * datapath_list: list of strings representing directories where information files will be searched in sequence
         * infofiles_path: same as datapath_list, used by validate, kept for compatibility
         * validate_path: string representing one unique path to validation schemas 
    
    """
    
    def __init__(self): 
        
        #DATAPATH = os.environ.get('OBSINFO_DATAPATH')
        
        datapath = ObsinfoConfiguration.Instance().obsinfo_datapath
        
        if not datapath:  
           warnings.warn("OBSINFO_DATAPATH not set, defaulting to working directory") 
           self.datapath_list = ["./"] # Use current directory as default.
        else:
           self.datapath_list = datapath
        
        self.infofiles_path = None
        self.validate_path = None

    def __str__(self):
        s = f'datapath_list: {self.datapath_list}\n'
        s += f'infofiles_path: {self.infofiles_path}\n'
        s += f'validate_path: {self.validate_path}'
        return s

    def build_datapath(self, file):
        """
        Create list of directories which may have data or schemas
        
        1) If the file path is absolute, return the file itself.
        2) If path starts by ./ or ../ complete to an absolute path using working directory
        3) If the file has no prefix discover whether file exists in the datapath list.
           Use the first found file.
           
        :param file: filename of file to be found
        :type file: str or path-like object
        :returns: found file as string
        :raises: FileNotFoundError
        """
        
        file, frag = urlparse.urldefrag(file)

        filestr = file if isinstance(file, str) else str(file)
        
        if not isinstance(file, Path):
            file = Path(file)
        
        if file.is_absolute(): 
            return filestr
    
        elif filestr[0:3] == "../" or filestr[0:2] == "./": # if path is absolute or relative to cwd:
            home = Path.cwd()
            self.datapath_list = str(Path.joinpath(home, file).resolve())
            return self.add_frag(self.datapath_list, frag)
                
        for dir in self.datapath_list:
             
            if gitLabFile.isRemote(dir):
                # This is done to avoid funny behaviour by pathlib
                slash = "/" if dir[-1] != "/" else ""
                fn = dir + slash + filestr
                
                if gitLabFile.get_gitlab_file(str(fn), False): #Check remote repository
                    self.datapath = fn
                    return Datapath.add_frag(self.datapath, frag) # Don't forget to add frag back! 
            else:             
                fn = (Path(dir).resolve()).joinpath(file)
                 
                if os.path.isfile(str(fn)): # Check local repository
                   self.datapath = str(fn)
                   return Datapath.add_frag(self.datapath, frag) # Don't forget to add frag back!
        
        raise FileNotFoundError(file)
    
    @staticmethod
    def add_frag(path, frag):
        """
        Add the path and the frag to restore a partial or complete uri
        
        :param path: path portion of uri, possibly with other elements but without frag
        :type path: str
        :param frag: fragment portion of uri
        :type frag: str
        :returns: path with frag as string
        """
        
        return path + ("#" + frag if frag else "")
    




        
        
        
