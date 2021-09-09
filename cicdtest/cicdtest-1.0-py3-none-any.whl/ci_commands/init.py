
"""
    Title: init.py
    Author: Akash D.
    Modified By: Kushagra A.
    Language: Python
    Date Created: 26-07-2021
    Date Modified: 03-09-2021
    Description:
        ###############################################################
        ## Starting file   ## 
         ###############################################################
 """

import requests
import json
import os 
import pathlib
import yaml
import click
from ci_commands import github_webhook, bitbucket_webhook, encrypt
from buildpan import setting


info = setting.info

# getting env variable
key = info["key"]
secret_key = info["secret_key"]
         
@click.command()
def init():
    '''
    For initiating the webhook operation 

    Please store config.yaml in the directory 
    Please create the clone of the repository  
    \f
    
   
    '''
    path=pathlib.Path().resolve()
    print("Your current directory  is : ", path)
    os.chdir(path)
    try:
        a_yaml_file = open("./config.yaml")
        parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
        project_id=parsed_yaml_file["project_id"]
        # print(project_id)

        response = requests.get("https://app.buildpan.com/api/v1/projects/detail/"+project_id)
        data = response.json()

        provider = data['project']["provider"]

        enc_key = b'CgOc_6PmZq8fYXriMbXF0Yk27VT2RVyeiiobUd3DzR4='
        
        # github access
        if provider == "github":
            name = data["project"]["repo"]["full_name"].split('/')
            token = data["project"]["githubtoken"]
            username = name[0]
            repo_name = name[1]

            dictionary ={
                "token" : token,
                "username" : username,
                "repo_name" : repo_name,
            }

            # Serializing json 
            json_object = json.dumps(dictionary, indent = 4)
        
            # Writing to sample.json
            with open(project_id+'.json',"w") as outfile:
                outfile.write(json_object)
        
            #Reading from json file
            with open(project_id+'.json') as file:
                info = json.load(file)
                username = info["username"]
                token = info["token"]
                repo_name = info["repo_name"]
            
            # encrypting a json file
            enc = encrypt.Encryptor()
            enc.encrypt_file(enc_key, project_id+'.json')

            github_webhook.github(project_id, path, token, username, repo_name)
        
        # bitbucket access
        elif provider == "bitbucket":
            name = data["project"]["repo"]["full_name"].split('/')
            token = data["project"]["repo"]["refresh_token"]
            username = name[0]
            repo_name = name[1]

            dictionary ={
                "refresh_token" : token,
                "username" : username,
                "repo_name" : repo_name,
            }
            # Serializing json 
            json_object = json.dumps(dictionary, indent = 4)
            
            # Writing to sample.json
            with open(project_id+'.json',"w") as outfile:
                outfile.write(json_object)
            
            # Reading from json file
            with open(project_id+'.json') as file:
                info = json.load(file)
                username1 = info["username"]
                refresh_token1 = info["refresh_token"]
                repo_name1 = info["repo_name"]

            # encrypting a json file
            enc = encrypt.Encryptor()
            enc.encrypt_file(enc_key, project_id+'.json')
            
            bitbucket_webhook.bitbucket(project_id, path, refresh_token1, key, secret_key, username1, repo_name1)
            

          
    except:
        print("config file not found")

# if __name__ == "__main__":
#     config = Configurator()

#     config.add_route(ENDPOINT, "/{}".format(ENDPOINT))
#     config.scan()

#     app = config.make_wsgi_app()
#     server = make_server("localhost", 80, app)
   
#     init()
   
#     server.serve_forever()


