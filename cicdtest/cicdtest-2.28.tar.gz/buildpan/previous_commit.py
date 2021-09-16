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
from buildpan import setting
import requests

info = setting.info

# getting env variable
get_sha = info["GET_SHA_URL"]


def prev_commit(path, repo_name):

    try:
        response = requests.get(get_sha, repo_name)
        res=response.content
        res=str(res)
        index=res.index("'")
        index1=res.index("'",index+1)
        res=res[index+1:index1]
        print(res)

        subprocess.call(["git", "fetch", "origin", res], cwd=path)
        subprocess.call(["git", "checkout", "FETCH_HEAD"], cwd=path)
    except:
        print("error")
