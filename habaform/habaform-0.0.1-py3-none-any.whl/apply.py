from requests.auth import HTTPBasicAuth
import requests
import os
from shutil import copyfile

cwd = os.getcwd()
current_habaform_file = cwd + '/habaform.hf'
old_habaform_file = cwd + '/DO_NOT_TOUCH/habaform.hf'

role_map = {
    "projectAdmin": 1,
    "maintainer":4,
    "developer":2,
    "guest":3,
    "limitedGuest":5
}

def check_for_project_existence(harbor_username,harbor_password,harbor_url,project_name):
    project_detail_url = '{}/api/v2.0/projects/{}'.format(harbor_url,project_name)
    r_status_code = requests.get(project_detail_url,auth=HTTPBasicAuth(harbor_username, harbor_password)).status_code
    if r_status_code == '200':
        print("Project {} not exist".format(project_name))
        return True
    else:
        print("Project {} not exist".format(project_name))
        return False
        

def delete_project(harbor_username,harbor_password,harbor_url,project_name):
    print("Deleting " + project_name)

    project_deletion_url = '{}/api/v2.0/projects/{}'.format(harbor_url,project_name)

    project_repos_url = '{}/api/v2.0/projects/{}/repositories?page=1&page_size=100'.format(harbor_url,project_name)
    r = requests.get(project_repos_url,auth=HTTPBasicAuth(harbor_username, harbor_password)).json()

    for repo_name in r:
        # repo_name is xxx/yyy, real_repo_name is yyy
        real_repo_name = repo_name['name'].split('/',1)[1]
        repo_deletion_url = '{}/api/v2.0/projects/{}/repositories/{}'.format(harbor_url,project_name,real_repo_name)
        print("Deleting " + repo_name['name'])
        r = requests.delete(repo_deletion_url,auth=HTTPBasicAuth(harbor_username, harbor_password)).json()
    
    r = requests.delete(project_deletion_url,auth=HTTPBasicAuth(harbor_username, harbor_password))

def create_project(harbor_username,harbor_password,harbor_url,project_name):
    print("Creating " + project_name)
    # Check for existence
    if check_for_project_existence(harbor_username,harbor_password,harbor_url,project_name):
        return
    
    project_creation_url = '{}/api/v2.0/projects'.format(harbor_url)
    project_json = {
    "project_name": project_name,
    "metadata": {
        "public": "true"
    },
    "storage_limit": -1
    }
    r = requests.post(project_creation_url,json=project_json,auth=HTTPBasicAuth(harbor_username, harbor_password))

def get_member_id_by_username(harbor_username,harbor_password,harbor_url,project_name,member_name):
    member_search_url = '{}/api/v2.0/projects/{}/members?page=1&page_size=100'.format(harbor_url,project_name)
    r = requests.get(member_search_url,auth=HTTPBasicAuth(harbor_username, harbor_password)).json()
    for member in r:
        if member['entity_name'] == member_name:
            return member['id']
    return

def delete_member(harbor_username,harbor_password,harbor_url,project_name,member_name):
    member_id = get_member_id_by_username(harbor_username,harbor_password,harbor_url,project_name,member_name)
    member_deletion_url = '{}/api/v2.0/projects/{}/members/{}'.format(harbor_url,project_name,member_id)
    r = requests.delete(member_deletion_url,auth=HTTPBasicAuth(harbor_username, harbor_password))

def add_member(harbor_username,harbor_password,harbor_url,project_name,member_name,member_role):
    member_add_url = '{}/api/v2.0/projects/{}/members'.format(harbor_url,project_name)
    member_role_id = role_map[member_role]
    member_json = {
    "role_id": member_role_id,
        "member_user": {
            "username": member_name
        }
    }
    r = requests.post(member_add_url,json=member_json,auth=HTTPBasicAuth(harbor_username, harbor_password))

def apply(harbor_username,harbor_password,harbor_url,habadiff_dict):

    # Delete projects
    for project_name in habadiff_dict['projects_change']['projects_to_be_deleted']:
        delete_project(harbor_username,harbor_password,harbor_url,project_name)

    # Create new projects
    for project_name in habadiff_dict['projects_change']['projects_to_be_added']:
        create_project(harbor_username,harbor_password,harbor_url,project_name)

    # Remove members from projects
    for project in habadiff_dict['project_members_change']:

        members_to_be_added = habadiff_dict['project_members_change'][project]['members_to_be_added']
        members_to_be_deleted = habadiff_dict['project_members_change'][project]['members_to_be_deleted']

        for member_name_with_role in members_to_be_deleted:
            real_member_name = member_name_with_role.split('(')[0]
            print("Deleting member " + real_member_name + " from " + project)
            delete_member(harbor_username,harbor_password,harbor_url,project,real_member_name)

        for member_name_with_role in members_to_be_added:
            real_member_name = member_name_with_role.split('(')[0]
            member_role = member_name_with_role.split('(')[1].split(')')[0]
            print("Adding member " + real_member_name + " to " + project)
            add_member(harbor_username,harbor_password,harbor_url,project,real_member_name,member_role)

    copyfile(current_habaform_file,old_habaform_file)