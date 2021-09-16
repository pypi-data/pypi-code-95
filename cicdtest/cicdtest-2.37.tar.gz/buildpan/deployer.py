"""
    Title: deployer
    Module Name: deployer
    Author: Abizer
    Modified By: Abizer
    Language: Python
    Date Created: 31-08-2021
    Date Modified: 02-09-2021
    Description: Return Type is Bolean Is success then "True" otherwise "False"
        ###############################################################
        ##                 Deployer for all Stack                    ## 
        ###############################################################
 """

import subprocess 
import logging
import json
import os

def mean_stack(cwd):
    '''
    Deploy MeanStack project
    '''

    success = False
    
    # Reding entrypoint 
    file_path = os.path.join(cwd,"package.json")
    print("file_path",file_path)
    package_file = open(file_path)
    project_detail = json.loads(package_file.read())
    print("loaded")
    package_file.close()

    # installing all the dependency if packge.json found otherwise genrate error
    result_install = subprocess.run("npm install", shell = True, stdout= subprocess.PIPE, stderr = subprocess.STDOUT)
    if result_install.returncode:
        print(result_install.stdout.decode())
        return success 
    else:
        # if pm2 is not installed installing otherwise update 
        result_install_pm2 = subprocess.run("npm install pm2 -g", shell = True, stdout= subprocess.PIPE, stderr = subprocess.PIPE)
        if result_install_pm2.returncode:
            print(result_install_pm2.stderr.decode()) 
            return success
        else:

            # check service status if off start that otherwise reload it 
            service_status = subprocess.run('pm2 status', shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            if service_status.stdout.decode().find("online") == -1:
                popen_arg = "pm2 start " + project_detail["main"]
                result_start = subprocess.run(popen_arg, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, cwd = cwd)
                process_fails = result_start.returncode
                print(result_start.stdout.decode()) 
            else:
                popen_arg = "pm2 reload " + project_detail["main"]
                result_relod = subprocess.run(popen_arg, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, cwd = cwd)
                process_fails = result_relod.returncode
                print(result_relod.stdout.decode()) 

        if process_fails:
            return success
        else: 
            success = True
            return success

def script_runer(scripts, path):
    '''
    Script runner is called when Script under jobs is called in workflow and have some script 
    that to be executed 
    
    '''
    print("path=", path)
    success = False
    for script in scripts:
        result = subprocess.run(script,shell= True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd = path)
    
        if result.returncode:
            return success
        
    success = True
    return success
    
    
            



