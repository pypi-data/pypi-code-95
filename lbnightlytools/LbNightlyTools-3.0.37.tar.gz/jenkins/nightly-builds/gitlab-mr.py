#!/bin/env python2

###############################################################################
# (c) Copyright 2019 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import gitlab
import json
import logging
import os
from pprint import pformat
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MRHook')

# Name of token we expect to be defined in the runtime environment
gitlab_token = 'GITLAB_TOKEN'

# These are the commands this script is designed to parse
build_cmd = '/ci-test'
rebuild_cmd = '/ci-retest'
rebuild_ref_cmd = '/ci-retest-ref'
rebuild_mr_cmd = '/ci-retest-mr'
cmd_keys = [build_cmd, rebuild_cmd, rebuild_ref_cmd, rebuild_mr_cmd]

# Will store a global reference against gitlab here
GITLAB_SERVER = None


def connect_gitlab():
    '''
    Method to allow cached lazy loading of the gitlab access
    '''

    global GITLAB_SERVER
    if GITLAB_SERVER is None:
        GITLAB_SERVER = gitlab.Gitlab('https://gitlab.cern.ch/',
                                      os.environ[gitlab_token])
    return GITLAB_SERVER


# Will store the result of looking up an MR and Project and gitlab here
CACHED_PROJS = {}
CACHED_MREQS = {}


def get_project_from_id(proj_id):
    '''
    Return the project corresponding to the given id

    @param proj_id: numerical id of the project that we want to get
    '''

    if proj_id not in CACHED_PROJS:
        gitlab_server = connect_gitlab()
        # Get the project the MR belongs to
        project = gitlab_server.projects.get(id=proj_id)
        CACHED_PROJS[proj_id] = project

    return CACHED_PROJS[proj_id]


def get_mr_from_id(proj_id, mreq_id):
    '''
    Return the merge request corresponding to the given id

    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''

    id_key = (proj_id, mreq_id)
    if id_key not in CACHED_MREQS:
        project = get_project_from_id(proj_id)
        mreq = project.mergerequests.get(id=mreq_id)
        CACHED_MREQS[id_key] = mreq

    return CACHED_MREQS[id_key]


def get_default_mr(proj_id, mreq_id):
    '''
    Get the project the MR belongs to

    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''
    project = get_project_from_id(proj_id)
    return project.attributes['path_with_namespace'] + '!' + str(mreq_id)


def get_default_platforms(proj_id, mreq_id):
    '''
    Return the platforms that we want to build

    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''

    gitlab_server = connect_gitlab()
    target = get_mr_from_id(proj_id, mreq_id).attributes['target_branch']

    target_dict = {
        'master': [
            'x86_64-centos7-gcc8-opt',
        ],
        'run2-patches': [
            'x86_64-slc6-gcc62-opt', 'x86_64-centos7-gcc62-opt',
            'x86_64-centos7-gcc7-opt'
        ],
        '2016-patches': [
            'x86_64-slc6-gcc62-opt',
        ],
        '2017-patches': [
            'x86_64-slc6-gcc62-opt', 'x86_64-centos7-gcc62-opt',
            'x86_64-centos7-gcc7-opt'
        ],
        '2018-patches': [
            'x86_64-slc6-gcc62-opt', 'x86_64-centos7-gcc62-opt',
            'x86_64-centos7-gcc7-opt'
        ]
    }

    # TODO potentially come up with some better way of derriving this
    return target_dict.get(target, [
        'x86_64-centos7-gcc8-opt',
    ])


def get_default_model(proj_id, mreq_id):
    '''
    Get the default model depending on the target branch of the MR

    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''

    # Need to connect to gitlab
    gitlab_server = connect_gitlab()
    target = get_mr_from_id(proj_id, mreq_id).attributes['target_branch']
    if target in [
            'master', 'run2-patches', '2016-patches', '2017-patches',
            '2018-patches'
    ]:
        return 'lhcb-' + target
    raise NotImplementedError()


def parse_build_args(command_args, proj_id, mreq_id):
    '''
    Parse the arguments passed to the command in the Gitlab comment and return

    @param command_args: list of strings containing the args passed to the gitlab command
    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''

    # Make sure the MR the command was submitted is present
    MR_IDs = []
    external_commits = []
    platforms = []
    # Make sure we're at least using the default model, allowing it to be overloaded
    model = get_default_model(proj_id, mreq_id)
    for i in command_args:
        if i.find("!") != -1:
            MR_IDs.append(i)
        if i.find("@") != -1:
            external_commits.append(i)
        if i.find('=') != -1:
            opt = i.split('=')[0]
            args = i.split('=')[1]
            for j in args.split(':'):
                if opt == 'platforms':
                    platforms.append(j)
                if opt == 'model':
                    model = j

    # Make sure only unique MR_IDs
    default_mr = get_default_mr(proj_id, mreq_id)
    if default_mr not in MR_IDs:
        MR_IDs.append(default_mr)
    if len(platforms) == 0:
        platforms = get_default_platforms(proj_id, mreq_id)

    return MR_IDs, external_commits, platforms, model


def parse_build_cmd(command_args, proj_id, mreq_id):
    '''
    Parse the build command and check for obvious errors

    @param command_args: list of strings containing the args passed to the gitlab command
    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''

    MR_IDs, external_commits, platforms, model = parse_build_args(
        command_args, proj_id, mreq_id)

    if len(MR_IDs) == 0:
        logger.error('Cannot launch a build when no MR is specified.')
        raise ValueError('Cannot launch a build when no MR is specified.')

    json_data = {
        'MR_IDs': MR_IDs,
        'external_commits': external_commits,
        'platforms': platforms,
        'model': model
    }

    return json_data


def find_previous_config(proj_id, mreq_id):
    '''
    Find the MR by searching for the last build command requested against the MR

    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''

    # Get the MR the command came from
    mr = get_mr_from_id(proj_id, mreq_id)

    # Get the comments associated with the MR
    mr_comments = mr.notes.list()

    comment_index = len(mr_comments)

    # Reverse iterate over the MR comments
    for comment in mr_comments[::-1]:
        if str(comment.body).find(build_cmd) != -1:
            logger.info("{}".format(comment.body))
            break
        comment_index = comment_index - 1

    if comment_index == 0:
        logger.error('Can not determine MR to re-build project')
        raise ValueError('Can not determine MR to re-build project')

    last_build_comment = mr_comments[comment_index]

    command_exe, command_args = find_command(last_build_comment)

    MR_IDs, external_commits, platforms, model = parse_build_args(
        command_args, proj_id, mreq_id)

    return MR_IDs, external_commits, platforms, model


def parse_rebuild_cmd(command_args, proj_id, mreq_id):
    '''
    This parses a command which is asking for a re-build of an MR

    @param command_args: list of strings containing the args passed to the gitlab command
    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    '''

    MR_IDs, external_commits, platforms, model = parse_build_args(
        command_args, proj_id, mreq_id)

    # TODO decide if we should allow a change in MR for a 're-build'?
    if len(MR_IDs) != 0:
        logger.error('Cannot rebuild with new MRs.')
        raise ValueError('Cannot rebuild with new MRs.')

    _MR_IDs, _external_commits, _platforms, _model = find_previous_config(
        proj_id, mreq_id)

    # For all of the parameters we can potentially need to be overload just one set for a rebuild
    # You have to be explicit when running the build command but it makes life easier
    if len(MR_IDs) != 0:
        _MR_IDs = MR_IDs
    if len(external_commits) != 0:
        _external_commits = commits
    if len(platforms) != 0:
        _platforms = platforms
    if len(model) != 0:
        _model = model

    return {
        'MR_IDs': _MR_IDs,
        'external_commits': _external_commits,
        'platforms': _platforms,
        'model': _model
    }


def find_command(command_string):
    '''
       This method looks for a command which is supported within the MR comment which triggered this hook
       This will raise an exception if a command is not found which this script can parse

    @param command_string:
    '''

    command_list = command_string.split(' ')

    i = 0
    for opt in command_list:
        if opt in cmd_keys:
            start = i
            break
        else:
            i = i + 1

    if i == len(command_list):
        logger.error('No command found.')
        raise ValueError('No command found.')

    command_exe = command_list[i]
    command_args = command_list[i + 1:]

    return command_exe, command_args


def send_gitlab_message(proj_id, mreq_id, message):
    '''
    This method posts a message against a MR in gitlab using an appropriate token.
    Only used to inform gitlab if a build has been requested or not.

    @param proj_id: numerical id of the project that we want to get
    @param mreq_id: numerical id of the merge request we want to get
    @param message: message to be sent to gitlab
    '''

    gitlab_server = connect_gitlab()
    mreq = get_mr_from_id(proj_id, mreq_id)

    mreq.notes.create({'body': message})


def remove_artifacts():
    '''
    Short method for cleaning up rogue artifacts
    '''

    for _file in ['gitlab-ref-build.txt', 'gitlab-mr-build.txt']:
        try:
            os.remove(_file)
        except:
            pass


def parse_raw_content(raw_content):
    '''
    Method to inspect the contents of the header from the gitlab hook and extract the useful data

    @param raw_content: Contents of header sent from gitlab hook
    '''

    content = json.loads(raw_content)

    command_string = content['object_attributes']['note']
    proj_id = int(content['merge_request']['target_project_id'])
    mreq_id = int(content['merge_request']['iid'])

    return command_string, proj_id, mreq_id


def construct_builds(raw_content):
    '''
    Main method which parses the gitlab hook and constructs the build artefacts to trigger further builds

    gitlab-ref-build.txt: file which is used to construct the environment to trigger the reference build for this MR
    gitlab-mr-build.txt:  file which is used to construct the environment to trigger the merge request itself be built

    @param raw_content: Contents of header sent from gitlab hook
    '''

    # Make sure artefacts don't exist before we start
    remove_artifacts()

    try:
        command_string, proj_id, mreq_id = parse_raw_content(raw_content)

    except Exception as err:
        logger.error('Failed to parse data from gitlab')
        logger.error('Error: {}'.format(err))
        # Cannot inform gitlab of the problem if we don't have both a proj_id and mreq_id
        raise

    command_exe, command_args = find_command(command_string)
    logger.info('Command Found: {}'.format(command_exe))
    logger.info('With Options: {}'.format(command_args))

    try:
        if command_exe == build_cmd:
            json_data = parse_build_cmd(command_args, proj_id, mreq_id)
        if command_exe in (rebuild_cmd, rebuild_ref_cmd, rebuild_mr_cmd):
            json_data = parse_rebuild_cmd(command_args, proj_id, mreq_id)
    except Exception as err:
        message = 'Failed to parse build command, no builds requested.\n'
        message += 'Error: {}'.format(err)
        # Let gitlab know there was an error parsing the instructions
        send_gitlab_message(proj_id, mreq_id, message)
        raise

    json_str = json.dumps(json_data)

    logger.info('JSON str: {}'.format(json_str))

    # Here we construct the files which construct the environment variables used to construct build jobs

    # TODO add some code to pass on to the build process the MR (commit?) that we should report back to in gitlab
    #
    #      this would be good to keep this minimal as the build process should only need to know where to send
    #      messages corresponding to builds completing successfully or failing
    #
    #      This will potentially just be an extension of MR_TOKEN but won't add until it's clear this can be passed to the main build code

    # MR-TOKEN:          This is a JSON object containing the important data to construct a gitlab build in LHCbNightConf
    # slots:             Corresponds to the slots name e.g. 'lhcb-master-ref', 'lhcb-2018-patches', ...
    # configs_branch:    The branch of LHCbNightlyConf to use
    # flavour:           Flavour of the test being run. 'testing' as we don't want to spam people when tests fail
    # platforms:         Space separated list of platforms we wish to build for

    if command_exe != rebuild_mr_cmd:
        logger.info('Writing: gitlab-ref-build.txt')
        with open('gitlab-ref-build.txt', 'w') as _file:
            _file.write('MR_TOKEN=' + json_str + '\n')
            _file.write('scripts_version=master\n')
            _file.write('slots=' + json_data['model'] + '-ref\n')
            _file.write('configs_branch=master\n')
            _file.write('flavour=testing\n')
            _file.write('platforms={}'.format(' '.join(
                json_data['platforms'])))

    if command_exe != rebuild_ref_cmd:
        logger.info('Writing: gitlab-mr-build.txt')
        with open('gitlab-mr-build.txt', 'w') as _file:
            _file.write('MR_TOKEN=' + json_str + '\n')
            _file.write('scripts_version=master\n')
            _file.write('slots=' + json_data['model'] + '-mr\n')
            _file.write('configs_branch=master\n')
            _file.write('flavour=testing\n')
            _file.write('platforms={}'.format(' '.join(
                json_data['platforms'])))

    message = 'Correctly parsed build command and have requested Reference and MR builds.\n\n'
    message += 'You can check their build progress here: https://lhcb-nightlies.web.cern.ch/testing/summary.\n\n'
    message += 'You can compare the builds using a URL like: https://lhcb-nightlies.web.cern.ch/testing/compare/lhcb-master-mr/MR-BUILD-ID/lhcb-master-ref/REF-BUILD-ID/\n'

    send_gitlab_message(proj_id, mreq_id, message)


# Check that the information from the webhook is present in the local env
if 'content' not in os.environ:
    logger.error("Cannnot find content from webhook, not attempting to run.")
    sys.exit(-1)

construct_builds(os.environ['content'])
