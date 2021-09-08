import gitlab
import urllib
import json
import base64
import re
import os
from pathlib import Path
from urllib import parse as urlparse
from urllib.parse import unquote
from urllib.request import urlopen
import logging
logger = logging.getLogger("obsinfo")

# obsinfo
from .configuration import ObsinfoConfiguration

# private token or personal token authentication


class gitLabFile(object):
    """
    Provide the methods to use the gitlab API to read a remote file and decode it
    
      **Attributes:**
     
       
       *None*
       
    """
      
    @staticmethod
    def get_gitlab_file(uri, read_file=True):
        """
        Get the file content pointed at by uri and decode it.
        
        Uses b64 first to get the remote file and convert to a byte string, 
        and then utf-8 to convert to regular string.
        
        :param uri: uri to read
        :type uri: string or path-like object
        :param read_file: If true, reads the content. If not, simply checks the file exists
        :returns: string of read content
        :raises: FileNotFoundError, ValueError
        
        """
        
        # Use configuration ifnormation
        gitlab_repository = ObsinfoConfiguration.Instance().gitlab_repository
        project_path = ObsinfoConfiguration.Instance().gitlab_project
        obsinfo_branch = ObsinfoConfiguration.Instance().obsinfo_branch
        
        if not gitlab_repository or not project_path:
            msg = "One or several environment variables, OBSINFO_GITLAB_REPOSITORY or \
                     OBSINFO_PROJECTPATH in the configuration file ~/.obsinforc, are missing"
            logger.error(msg)
            raise ValueError(msg)
        
        with gitlab.Gitlab(gitlab_repository) as gl:
        
            project = gl.projects.get(project_path)
            if not project:
                msg = f'Project not found in repository: {project_path}'
                logger.error(msg)
                raise FileNotFoundError(msg)    
            
            if urlparse.urlsplit(uri).scheme: #Sometime it comes with scheme, sometimes not
                uri = urlparse.urlsplit(uri).path
                pattern = "/"
            else:
                # Remove elements from path
                pat1 = re.compile("http://")
                pat2 = re.compile("https://")
                if pat1.match(gitlab_repository):
                    gitlab_repository = pat1.sub("", gitlab_repository)
                if pat2.match(gitlab_repository):
                    gitlab_repository = pat2.sub("", gitlab_repository)
                
                pattern = ("/" if gitlab_repository[0] != "/" else "") + gitlab_repository 
            
                if gitlab_repository[-1] != "/":
                    pattern += "/"
            
            #we assume project_path has no leading slash
            pattern += project_path
            if project_path[-1] != "/":
                pattern += "/"
                          
            uri = re.sub(pattern, "", uri) # remove everything but path relative to project path
            
            try:
                f = project.files.get(file_path=uri, ref=obsinfo_branch)
                if not read_file:
                    return True
            except gitlab.exceptions.GitlabOperationError:
                if read_file:
                    msg = f'Error reading remote (gitlab) file: {uri}'
                    print(msg)
                    raise FileNotFoundError(msg)               
                else:
                    return None
            # get the decoded content. Two decodes are necessary, from 8character string to bytes and 
            # from bytes to a python string using utf-8
            bytecontent = base64.b64decode(f.content)
            ret = bytecontent.decode("utf-8")

        return ret
    
    @staticmethod
    def isRemote(file):
        """
        Checks if scheme means file is remote.
        
        :param file: filename to be checked, with complete uri
        :type file: str
        :returns: boolean. True if remote, False otherwise
        """
        return re.match('^http:', file) or re.match('^https:', file)


