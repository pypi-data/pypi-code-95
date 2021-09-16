"""
    Title: github_webhook.py
    Author: Akash D.
    Modified By: Kushagra A.
    Language: Python
    Date Created: 26-07-2021
    Date Modified: 13-09-2021
    Description:
        ###############################################################
        ## Create a webhook on a specific repository   ## 
         ###############################################################
 """

from buildpan.installer import installer
from logging import info
import os
from github import Github
from buildpan import setting, create_file



ENDPOINT = "webhook"

info = setting.info

fetch_log = info["FETCH_LOG_URL"]
host = info["HOST"]
         
def github(project_id, path, token, username, repo_name):
    
    try:
        
        # Before creating
        dir_list = os.listdir(path) 
        print("List of directories and files before creation:")
        print(dir_list)
        print()
        
        # access_token =token # access token of github account 
        # OWNER = username  # github account name
        # REPO_NAME =repo_name # github repository name
        EVENTS = ["*"]      # Events on github
        # HOST = host  # server ip (E.g. - ngrok tunnel)
       
    
        config = {
            "url": f"http://{host}/{ENDPOINT}",
            "content_type": "json"
        }
    
        # login to github account
        print(token)
        g = Github(token)
        print("1")
        print(f"{username}/{repo_name}")
        # accessing a particular repository of a account
        repo = g.get_repo(f"{username}/{repo_name}")
        print("2")
        print(repo)


        # creating a webhook on a particular repository
        try:
            repo.create_hook("web", config, EVENTS, active=True)

            installer()
            # create file
            create_file.create_file(project_id, repo_name, path, username)

          
        except:
            print("webhook already exists on this repository ")
            
            installer()

            # create file
            create_file.create_file(project_id, repo_name, path, username)

          
    except Exception as e:
        print("exception occured = ", e)


