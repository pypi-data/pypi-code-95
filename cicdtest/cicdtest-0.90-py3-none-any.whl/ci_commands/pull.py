"""
    Title: pull.py
    Author: Kushagra A.
    Language: Python
    Date Created: 31-08-2021
    Date Modified: 03-09-2021
    Description:
        ###############################################################
        ## Create a webhook on a specific bitbucket repository   ## 
         ###############################################################
 """

import requests
import git
import os
import time
import datetime
from buildpan import setting


info = setting.info


# getting env variable
loop = info["TIME"]
push_commit = info["PUSH_COMMIT_URL"]
fetch_log = info["FETCH_LOG_URL"]

def pull(repo_name, path, project_id, username):
     #   pull
            for i in range(int(loop)):
                params = {
                    'repository': repo_name
                }
                # print(params)
                response = requests.get(push_commit, params)
                print('Response from server',response) 
                res=response.content
                res=str(res)
                index=res.index("'")
                index1=res.index("'",index+1)
                res=res[index+1:index1]
                repo_name = repo_name.lower()
                res = res.lower()
                print(res)
                print(repo_name)

                if res == repo_name:
                    print("commit found for repo ",res) 
                    # val=len(res)
                    repo = git.Repo(path)
                    origin = repo.remote(name='origin')
                    res=origin.pull()
                    print("Looking for Pull Opeartion")
                    time.sleep(60)
                    print("done")
                    curtime = datetime.datetime.now()          
                    response2 = requests.post(fetch_log,data={'project_id':project_id,'repo_name':repo_name,'Time ':curtime,'user_name':username,'message':"pull success",'status':'pull operation performed'}) 

                    val=0
                else:
                    print("no files to pull")
                    time.sleep(60)
                    curtime = datetime.datetime.now()          
                    response2 = requests.post(fetch_log,data={'project_id':project_id,'repo_name':repo_name,'Time ':curtime,'user_name':username,'message':"pull failed",'status':'pull operation performed'})
 