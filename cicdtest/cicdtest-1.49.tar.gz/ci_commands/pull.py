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
import click


info = setting.info


# getting env variable
loop = info["TIME"]
push_commit = info["PUSH_COMMIT_URL"]
fetch_log = info["FETCH_LOG_URL"]


@click.command()
def pull():
    # pull

    all_repo_name = []

    with open("/home/kush/cron_test/buildpan_test/info.txt") as file:
        info = file.readlines()
        for data in info:
            d = eval(data)
            repo_name = d["repo_name"]
            repo_name = repo_name.lower()
            all_repo_name.append(repo_name)
            path = d["path"]
 

    response = requests.get(push_commit)
    res=response.content
    res=str(res)
    index=res.index("'")
    index1=res.index("'",index+1)
    res=res[index+1:index1]
    res = res.lower()


    for repo in all_repo_name:

        if str(repo) == res:


            log = f"commit found for repo {repo}" 
            repo = git.Repo(path)
            origin = repo.remote(name='origin')
            res=origin.pull()

                #     curtime = datetime.datetime.now()          
                #     response2 = requests.post(fetch_log,data={'project_id':project_id,'repo_name':repo_name,'Time ':curtime,'user_name':username,'message':"pull success",'status':'pull operation performed'}) 

        else:
            log = "no files to pull"
                #     curtime = datetime.datetime.now()          
                #     response2 = requests.post(fetch_log,data={'project_id':project_id,'repo_name':repo_name,'Time ':curtime,'user_name':username,'message':"pull failed",'status':'pull operation performed'})
    
    with open("process.txt", "a") as file:
        file.write(log)



