import requests
import yaml
import os
import sys
from os import path
from shutil import copyfile

from requests.auth import HTTPBasicAuth

cwd = os.getcwd()
current_habaform_file = cwd + '/habaform.hf'
old_habaform_file = cwd + '/DO_NOT_TOUCH/habaform.hf'

def parse(harbor_username, harbor_password, harbor_url):
    global_project_list = []
    project_list_url = '{}/api/v2.0/projects?page=1&page_size=100'.format(harbor_url)
    r = requests.get(project_list_url).json()
    for project in r:
        each_project = {}
        
        project_id = project['project_id']
        project_member_username_list = []
        project_member_list_url = '{}/api/v2.0/projects/{}/members?page=1&page_size=100'.format(harbor_url,project_id)
        r = requests.get(project_member_list_url,auth=HTTPBasicAuth(harbor_username, harbor_password)).json()
        for user in r:
            project_member_username_list.append('{}({})'.format(user['entity_name'],user['role_name']))
        each_project[project['name']] = {'members':project_member_username_list}
        global_project_list.append(each_project)

    yaml_data_dict = {}
    yaml_data_dict['habaformVersion'] = 1
    yaml_data_dict['projects'] = global_project_list
    with open(current_habaform_file,'w') as f:
        doc = yaml.dump(yaml_data_dict,f)

    if not path.exists(current_habaform_file):
        sys.exit("habaform.hf not found.")
    if not path.exists(old_habaform_file):
        print('Old habaform file not found, creating one for you.')
        os.makedirs('DO_NOT_TOUCH')
        copyfile(current_habaform_file,old_habaform_file)
    
    print("Parse complete, check your {}/habaform.hf and start habaforming!".format(cwd))