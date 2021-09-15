"""
    Title: previous_commit
    Author: Kushagra A.
    Language: Python
    Date Created: 14-09-2021
    Date Modified: 14-09-2021
    Description:
        ###############################################################
        ## Get previous commit of a repository   ## 
         ###############################################################
 """

import subprocess

def prev_commit(path, sha):
    subprocess.call(["git", "fetch", "origin", "edf3c8c2708213a736c54b2175d1241094f920b7"], cwd=path)
    subprocess.call(["git", "checkout", "FETCH_HEAD"], cwd=path)

