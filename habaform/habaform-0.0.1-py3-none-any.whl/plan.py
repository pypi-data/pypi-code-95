import os
from os import path
import yaml

cwd = os.getcwd()
current_habaform_file = cwd + '/habaform.hf'
old_habaform_file = cwd + '/DO_NOT_TOUCH/habaform.hf'

def check_habafile_diff(old_habaform_file,current_habaform_file):
    with open(old_habaform_file, 'r') as f:
        old_habaform_file_content = yaml.safe_load(f)
    with open(current_habaform_file, 'r') as f:
        current_habaform_file_content = yaml.safe_load(f)
    
    old_habaform_project_with_member_dict = {}
    current_habaform_project_with_member_dict = {}

    for project in old_habaform_file_content['projects']:
        old_habaform_project_with_member_dict[list(project.keys())[0]] = project[list(project.keys())[0]]['members']
    for project in current_habaform_file_content['projects']:
        current_habaform_project_with_member_dict[list(project.keys())[0]] = project[list(project.keys())[0]]['members']

    project_member_change_dict = {}
    for project_name, project_members in current_habaform_project_with_member_dict.items():

        if project_name in old_habaform_project_with_member_dict:
            old_member_list = old_habaform_project_with_member_dict[project_name]
        else:
            # If there is a new project
            old_member_list = []
        current_member_list = current_habaform_project_with_member_dict[project_name]
        members_to_be_deleted_list = list(set(old_member_list).difference(set(current_member_list)))
        members_to_be_added_list = list(set(current_member_list).difference(set(old_member_list)))
        # Check if there is a change
        if len(members_to_be_added_list) or len(members_to_be_deleted_list):
            project_member_change_dict[project_name] = {"members_to_be_added":members_to_be_added_list,"members_to_be_deleted":members_to_be_deleted_list}

    # Checking for projects change
    old_habaform_project_list = []
    for project in old_habaform_file_content['projects']:
        for key in project.keys():
            old_habaform_project_list.append(key)

    current_habaform_file_project_list = []
    for project in current_habaform_file_content['projects']:
        for key in project.keys():
            current_habaform_file_project_list.append(key)

    projects_to_be_deleted_list = list(set(old_habaform_project_list).difference(set(current_habaform_file_project_list)))
    projects_to_be_added_list = list(set(current_habaform_file_project_list).difference(set(old_habaform_project_list)))

    habadiff_dict = {}
    habadiff_dict['projects_change'] = {"projects_to_be_deleted":projects_to_be_deleted_list,"projects_to_be_added":projects_to_be_added_list}
    habadiff_dict['project_members_change'] = project_member_change_dict
    return habadiff_dict

def format_diff(habadiff_dict):
    print("During this plan, the following changes will be made:")

    print("The following projects will be deleted: " + ','.join([str(project_name) for project_name in habadiff_dict['projects_change']['projects_to_be_deleted']]))
    print("The following projects will be created: " + ','.join([str(project_name) for project_name in habadiff_dict['projects_change']['projects_to_be_added']]))

    for project_name, member_change in habadiff_dict['project_members_change'].items():
        if len(member_change['members_to_be_added']):
            print("Project " + project_name + " will add these members: " + ','.join([str(member) for member in member_change['members_to_be_added']]))
        if len(member_change['members_to_be_deleted']):
            print("Project " + project_name + " will remove these members: " + ','.join([str(member) for member in member_change['members_to_be_deleted']]))

def plan(harbor_username,harbor_password,harbor_url):
    habadiff_dict = check_habafile_diff(old_habaform_file,current_habaform_file)
    format_diff(habadiff_dict)
    return habadiff_dict