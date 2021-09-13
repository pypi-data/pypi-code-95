"""
    Title: github_webhook.py
    Author: Akash D.
    Modified By: Kushagra A.
    Language: Python
    Date Created: 26-07-2021
    Date Modified: 11-09-2021
    Description:
        ###############################################################
        ## Create a webhook on a specific repository   ## 
         ###############################################################
 """

from logging import info
import os
from github import Github
from buildpan import setting, create_file



ENDPOINT = "webhook"

info = setting.info

fetch_log = info["FETCH_LOG_URL"]
         
def github(project_id, path, token, username, repo_name):
    
    try:
        
        # Before creating
        dir_list = os.listdir(path) 
        print("List of directories and files before creation:")
        print(dir_list)
        print()
   

        access_token =token # access token of github account 
        OWNER = username  # github account name
        REPO_NAME =repo_name # github repository name
        EVENTS = ["*"]      # Events on github
        HOST = os.getenv('HOST')  # server ip (E.g. - ngrok tunnel)
    
        config = {
            "url": "http://{host}/{endpoint}".format(host=HOST, endpoint=ENDPOINT),
            "content_type": "json"
        }
    
        # login to github account
        g = Github(access_token)

        # accessing a particular repository of a account
        repo = g.get_repo("{owner}/{repo_name}".format(owner=OWNER, repo_name=REPO_NAME))
        print(repo)


        # creating a webhook on a particular repository
        try:
            repo.create_hook("web", config, EVENTS, active=True)

            # create file
            create_file.create_file(project_id, repo_name, path, username)

          
        except:
            print("webhook already exists on this repository ")

            # create file
            create_file.create_file(project_id, repo_name, path, username)

          
    except:
        print("exception occured")


