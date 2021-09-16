"""
    Title: platforminstaller
    Module Name: platforminstaller
    Author: Abizer
    Modified By: Abizer
    Language: Python
    Date Created: 4-09-2021
    Date Modified: 07-09-2021
    Description: diffrent platform installer to be called at init process  
        ###############################################################
        ##                 platform installer                        ## 
        ###############################################################
 """
import subprocess

def node_installer(node_ver):
    '''
    node installer this function to be called for Linux machine 

    '''
    print("called")
    subprocess.run("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash", shell= True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.run("source ~/.nvm/nvm.sh", shell= True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("1")
    
    popen_arg = "nvm install "+ node_ver 
    subprocess.run(popen_arg ,shell= True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("2")

    if node_ver != "latest":
        popen_arg = "nvm use "+ node_ver
        subprocess.run(popen_arg ,shell= True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    print("done")
