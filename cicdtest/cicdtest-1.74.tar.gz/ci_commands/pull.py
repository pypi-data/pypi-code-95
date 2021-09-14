"""
    Title: pull.py
    Author: Kushagra A.
    Language: Python
    Date Created: 31-08-2021
    Date Modified: 11-09-2021
    Description:
        ###############################################################
        ## Check for pull operation on a repository   ## 
         ###############################################################
 """

from buildpan.previous_commit import prev_commit
import requests
import git
import os
import time
import datetime
from buildpan import setting, workflow, repo_pull
import click


info = setting.info


# getting env variable
push_commit = info["PUSH_COMMIT_URL"]


@click.command()
def pull():
    '''
    For initiating the pull operation

    \f
    '''
    
    # pull

    all_repo_name = []

    with open("/home/kush/cron_test/buildpan_test/info.txt") as file:
        info = file.readlines()
        for data in info:
            d = eval(data)
            repo_name = d["repo_name"]
            repo_name = repo_name.lower()
            all_repo_name.append(repo_name)
    
    params = {
        "repo_name": all_repo_name
    }
    

    response = requests.get(push_commit, params)
    res=response.content
    res=str(res)
    index=res.index("'")
    index1=res.index("'",index+1)
    res=res[index+1:index1]
    res = res.lower()

    for repo in all_repo_name:

        if str(repo) == res:

            with open("/home/kush/cron_test/buildpan_test/info.txt") as file:
                info = file.readlines()
                for data in info:
                    d = eval(data)
                    repo_name = d["repo_name"]
                    repo_name = repo_name.lower()

                    if repo == repo_name:
                        path = d["path"]
                        project_id = d["project_id"]
                        username = d["username"]

                        repo_pull.repo_pull(path, project_id, repo, username)
                        
                        log = f"pull operation successful for {repo_name}"

                        response = workflow.workflow(path)

                        if response == False:
                            prev_commit(path)
 

    with open("process.txt", "a") as file:
        file.write(log + "\n")



