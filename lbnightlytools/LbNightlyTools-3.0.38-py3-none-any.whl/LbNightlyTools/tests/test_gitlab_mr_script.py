##############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import os
import json
from copy import deepcopy

from LbNightlyTools.Scripts import GitlabMR

_testdata = os.path.normpath(
    os.path.join(*([__file__] + [os.pardir] * 4 + ['testdata'])))
with open(os.path.join(_testdata, 'ci-test-hook-content.json')) as f:
    _hook_content = json.load(f)


def test_get_hook_args():
    args = GitlabMR.get_hook_args(_hook_content)
    assert args.sources == ['lhcb/Rec!1753']
    assert not args.merge


def test_gitlab_feedback():
    if not os.environ.get('GITLAB_TOKEN'):
        # for some reason getting a note requires a token
        return
    source = GitlabMR.get_hook_trigger(_hook_content)
    note, discussion = GitlabMR.gitlab_note_discussion(source)
    assert hasattr(note, 'awardemojis')
    assert hasattr(discussion, 'notes')


def test_main():
    GitlabMR.get_main_job_config([
        'gaudi/Gaudi!123', 'lhcb/LHCb@v50r6', 'lhcb-datapkg/TCK/HltTCK!5',
        '--platforms=x86_64-centos7-gcc8-opt,x86_64-centos7-gcc8-dbg'
    ])
    try:
        # projects without namespaces should fail
        GitlabMR.get_main_job_config(['LHCb!123'])
        assert False
    except GitlabMR.TriggerError:
        pass

    try:
        # bare MRs should fail
        GitlabMR.get_main_job_config(['!123'])
        assert False
    except GitlabMR.TriggerError:
        pass

    try:
        # multiple sources for a project
        GitlabMR.get_main_job_config(['gaudi/Gaudi!123', 'gaudi/Gaudi!456'])
        assert False
    except GitlabMR.TriggerError:
        pass

    try:
        # non-existant project
        GitlabMR.get_main_job_config(['lhcb/Foo!123'])
        assert False
    except GitlabMR.TriggerError:
        pass

    try:
        # non-existant MR
        GitlabMR.get_main_job_config(['lhcb/LHCb!1234567'])
        assert False
    except GitlabMR.TriggerError:
        pass

    try:
        # non-existant commit
        GitlabMR.get_main_job_config(['lhcb/LHCb@1234567890abcdef'])
        assert False
    except GitlabMR.TriggerError:
        pass

    try:
        GitlabMR.get_main_job_config(['--help'])
    except SystemExit:
        # TODO test stdout here
        pass


def test_main_with_hook():
    hook_var = 'TEST_MAIN_WITH_HOOK'
    args = ['--hook-var=' + hook_var]

    os.environ[hook_var] = json.dumps(_hook_content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert config['sources'] == ['lhcb/Rec!1753']
    assert not config['merge']

    content = deepcopy(_hook_content)

    # support full URLs to Gitlab
    content["object_attributes"]["note"] = (
        '/ci-test https://gitlab.cern.ch/lhcb/LHCb/-/merge_requests/111')
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert 'lhcb/LHCb!111' in config['sources']

    # deduce group when not specified
    content["object_attributes"]["note"] = '/ci-test LHCb!111'
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert 'lhcb/LHCb!111' in config['sources']

    # deduce group/project when not specified
    content["object_attributes"]["note"] = '/ci-test !111'
    os.environ[hook_var] = json.dumps(content)
    try:
        config = GitlabMR.get_main_job_config(args)[0]
        assert False
    except GitlabMR.TriggerError as e:
        message = str(e)
        assert 'lhcb/Rec!1753' in message and 'lhcb/Rec!111' in message
        assert 'Some projects given multiple times' in message

    # deduce group/project when not specified
    content["object_attributes"]["note"] = '/ci-test --merge !111'
    os.environ[hook_var] = json.dumps(content)
    try:
        config = GitlabMR.get_main_job_config(args)[0]
        assert False
    except GitlabMR.TriggerError as e:
        message = str(e)
        assert 'lhcb/Rec!1753' in message and 'lhcb/Rec!111' in message
        assert 'is already merged' in message

    # throw an exception when parser fails
    content["object_attributes"]["note"] = '/ci-test --garbage'
    os.environ[hook_var] = json.dumps(content)
    try:
        GitlabMR.get_main_job_config(args)
    except GitlabMR.TriggerError as e:
        assert 'unrecognized argument' in str(e)

    # throw an exception when parser fails
    content["object_attributes"]["note"] = '/ci-test garbage'
    os.environ[hook_var] = json.dumps(content)
    try:
        GitlabMR.get_main_job_config(args)
    except GitlabMR.TriggerError as e:
        assert 'is not a valid source specification' in str(e)

    # support for usage (--help) message
    content["object_attributes"]["note"] = '/ci-test --help'
    os.environ[hook_var] = json.dumps(content)
    try:
        GitlabMR.get_main_job_config(args)
    except GitlabMR.TriggerError as e:
        message = str(e)
        assert (message.startswith('usage:')
                and 'positional arguments' in message)

    del os.environ[hook_var]
