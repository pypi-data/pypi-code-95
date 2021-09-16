#!/usr/bin/env python
###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import datetime
import gitlab
import json
import logging
import os
import re
from collections import defaultdict
from gitlab.v4.objects import (ProjectMergeRequest as MergeRequest,
                               ProjectCommit as Commit)
from itertools import chain
from .Configuration import (cloneSlot, Project, slot_factory, DataProject,
                            Package)
from .GitlabUtils import _gitlabServer, _getGitlabProject, cached

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def full_name(project_or_package):
    '''
    Return the full GitLab path for a project or a package.
    '''
    # TODO use something from LbNightlyTools?
    name = project_or_package.name
    if isinstance(project_or_package, Project):
        namespace = 'gaudi' if name == 'Gaudi' else 'lhcb'
    else:
        namespace = 'lhcb-datapkg'
    return namespace + '/' + name


def gitlab_link(obj):
    '''
    Construct a html link for a GitLab MR or commit object.

    @param obj: MergeRequest or Commit object
    '''
    if isinstance(obj, MergeRequest):
        ref = obj.attributes['references']['short']
    elif isinstance(obj, Commit):
        ref = '@' + obj.attributes['short_id']
    else:
        raise TypeError('Unsupported gitlab object')
    return '<a href="{}" target="_blank">{}{}</a>'.format(
        obj.attributes['web_url'], obj.project.attributes['name'], ref)


def mr_getrefdate(mrs):
    '''
    Return the newest date that any MR was forked from it's target branch
    The value returned is to the second so is sufficient to lookup the git ref of all external projects at that time

    @param mrs: This is a list of (mr, project) which are the gitlab objects
    '''
    # Get the latest date that the given MRs were forked at.
    # This is used to know what to do with projects we've not explicitly included in the build slot
    # e.g. if we depend on LHCb forked at date X we will want to take the last Gaudi master commit before this

    mr_ref_dates = []
    # Loop through all MRs
    for mr in mrs:
        # Parse the date of the time when the MR was committed
        ref_sha1 = mr.attributes['diff_refs']['base_sha']
        # TODO should we get the next (first) commit's time? With for example:
        #      sorted(mr.commits(), key=lambda c: c.attributes['commited_date'])[0]
        committed_date = mr.project.commits.get(
            ref_sha1).attributes['committed_date']
        committed_date = committed_date.rstrip('Z')
        if '+' in committed_date:
            committed_date = committed_date.split('+', 1)[0]
        mr_ref_dates.append(
            datetime.datetime.strptime(committed_date, "%Y-%m-%dT%H:%M:%S.%f"))

    # Return the latest time corresponsing to the last MR branched from it's project
    return sorted(mr_ref_dates)[-1].isoformat()


def clone_slot(parent_slot, slot_name, slot_desc, platforms):
    '''
    Constructs a new Slot object and returns it after re-configuring it

    @param parent_slot: this is the slot we're supposed to use as a reference to construct a new one
    @param slot_name: this is the name the new slot will have
    @param slot_desc: this is the description applied to the new slot
    @param platforms: this is a comma separated list of platforms the new slot is to be built against
    '''
    # Clone from a given slot and define some common parameters
    new_slot = cloneSlot(parent_slot, slot_name)
    new_slot.desc = slot_desc
    if platforms:
        new_slot.platforms = []
        new_slot.platforms.extend(platforms.split(','))
    return new_slot


def slot_repos(slot, with_disabled=False):
    '''
    Return a flat dict with non-disabled projects and packages.
    '''
    repos = {}
    for project in slot.projects:
        if not with_disabled and project.disabled:
            continue
        if isinstance(project, DataProject):
            for package in project.packages:
                assert package.name not in repos
                repos[package.name] = package
        else:
            assert project.name not in repos
            repos[project.name] = project
    return repos


@cached
def getLastCommit(project, ref_date, branch):
    '''
    Return the most recent commit id from a project on a branch before a
    given date.
    '''
    project = _getGitlabProject(project)
    branch = 'master' if branch.lower() == 'head' else branch
    # TODO here we rely on gitlab reverse ordering the commits
    commit = project.commits.list(until=ref_date, ref_name=branch)[0]
    return commit.attributes['id']


def set_last_commits(slot, ref_date, commits):
    '''
    This method sets the external commit ids for all of the projects.
    This is either the commit corresponding to the time of the last MR fork (this date is defined as ref_date)
    or, the commit of the project as defined in the external_commits dictionary

    @param build_slot: This is the Slot object we want to define the projects for
    @param ref_date: This is the date which is taken to be the time when the last MR was forked
    @param commits: This is the dictionary containing the external_commit refs with project_names as keys
    '''
    for name, p in list(slot_repos(slot).items()):
        try:
            commit = commits[name]
        except KeyError:
            commit = getLastCommit(full_name(p), ref_date, p.version)

        logger.debug("Setting checkout for '{}' to be '{}'".format(
            name, commit))
        p.checkout_opts['commit'] = commit


def _find_slot(slots, name):
    found = [s for s in slots if s.name == name]
    assert len(found) == 1, 'Expected exactly one slot, got {!r}'.format(found)
    return found[0]


def get_model_slot(target_branch, slots):
    '''
    Return the Slot which we use as a model for the ref and test builds.

    @param target_branch: Target branch of the MR.
    @param slots: Model slots to pick from.
    '''

    # This copies the reference Slot from the target branch, i.e. master, lhcb-patches-2018, etc
    if target_branch == 'master':
        return _find_slot(slots, 'lhcb-master')
    elif target_branch == 'run2-patches':
        return _find_slot(slots, 'lhcb-run2-patches')
    message = ('Cannot determine Slot configuration from target branch "{}".'.
               format(target_branch))
    logger.error(message)
    raise NotImplementedError(message)


def create_mr_slots(sources, platforms, merge, model_slots):
    '''
    Constructs and returns two new Slot objects.

    The first is the reference slot, while the second is the testing
    slot, based on the MRs/commits/branches specified with `sources`.
    The model slot is picked from `model_slots` based on the target
    branch of MRs, which must all be consistent.

    In case of "branch" mode (`merge` is False), the newest date that
    any MR in `sources` was forked from its target branch is determined.
    For projects not specified in `sources` ("external" projects), the
    last commit on the target branch before that date is used.

    In case of "integration" mode (`merge` is True), the target branch
    of unspecified projects is taken, while for MRs in `sources` a
    merge with the target branch is requested. This matches the usual
    nightly behaviour.

    @param sources: A list of ids of the merge requests to be included
    in the MR build, e.g. ['lhcb/Rec!1753', 'lhcb/LHCb@2ad1a811'].
    @param platforms: Comma separated string of platforms that these
    slots are to request builds for.
    @param merge: Use integration mode (tip of target branch + MRs).
    @model_slots: Model slots to choose from.
    '''

    # Split sources per project, classify into "commits" (str) and MRs,
    # and fetch MRs
    project_sources = defaultdict(list)
    for source in sources:
        m = re.match(r'(?P<path>.+/(?P<name>[^/]+))(?P<type>[!@])(?P<id>.*)',
                     source)
        if not m:
            raise ValueError('Unexpected source {!r}'.format(source))
        name = m.group('name')
        path = m.group('path')
        gp = _getGitlabProject(path)
        if m.group('type') == '!':
            obj = gp.mergerequests.get(m.group('id'))
        elif m.group('type') == '@':
            obj = gp.commits.get(m.group('id'))
        obj.project = gp
        obj.project_path = path
        project_sources[name].append(obj)

    # Check for conflicting sources
    mrs = [
        s for s in chain.from_iterable(list(project_sources.values()))
        if isinstance(s, MergeRequest)
    ]
    if not mrs:
        # need at least one MR to determine target branch and model slot
        raise ValueError('Must have at least one MR in sources')
    if not merge:
        # Collect all commits by resolving the heads of MRs
        ref_commits = {}
        commits = {}
        for name, ss in list(project_sources.items()):
            if not len(ss) == 1:
                raise ValueError('Must have at most one source per project in '
                                 'branch (no --merge) mode')
            if isinstance(ss[0], MergeRequest):
                commits[name] = ss[0].attributes['sha']
                ref_commits[name] = ss[0].attributes['diff_refs']['base_sha']
            else:
                commits[name] = ss[0].attributes['id']
                # TODO get a ref_commit from branching point with target?
        # Find the date of the last branch for any of the given MRs
        # TODO support commits here (find branching point with compare)
        ref_date = mr_getrefdate(mrs)
        logger.info('Will attempt to grab target branch for unspecified '
                    'projects as of: {}'.format(ref_date))
    else:
        merges = defaultdict(list)
        commits = {}
        for name, ss in list(project_sources.items()):
            for source in ss:
                if isinstance(source, MergeRequest):
                    merges[name].append(source.attributes['iid'])
                else:
                    if name in commits:
                        raise ValueError('Must have at most one commit source '
                                         'per project.')
                    commits[name] = source.attributes['id']

    # Obtain the target branch
    target_branches = set(mr.attributes['target_branch'] for mr in mrs)
    if len(target_branches) > 1:
        raise RuntimeError('Refuse to create slot with inconsistent target '
                           'branches: {}'.format(target_branches))
    target_branch = target_branches.pop()

    logger.info('Getting model slot')
    model_slot = get_model_slot(target_branch, model_slots)
    model_name = model_slot.name
    logger.info('Model slot is: {}'.format(model_name))

    logger.info('Creating Ref Slot')
    logger.info('name: {}'.format(model_name + '-ref'))
    ref_slot = clone_slot(model_slot, model_name + '-ref', 'MR reference slot',
                          platforms)
    ref_repos = slot_repos(model_slot, with_disabled=True)
    # If some sources are not in the slot definition, add them
    for name, ss in list(project_sources.items()):
        if name not in ref_repos:
            if ss[0].project_path.startswith('lhcb-datapkg/'):
                logger.info(
                    'Adding package "{}" to the slots based on {}.'.format(
                        name, model_name))
                ref_slot.projects['DBASE'].packages.append(
                    Package(name, target_branch))
            else:
                logger.warning(
                    'The project "{}" was not in the model slot {}. '
                    'Adding anyway.'.format(name, model_name))
                ref_slot.projects.append(Project(name, target_branch))
        else:
            ref_repos[name].disabled = False
    if not merge:
        # Set ref commits for tested projects and freeze "external" projects
        set_last_commits(ref_slot, ref_date, ref_commits)

    logger.info('Creating Test Slot')
    logger.info('name: {}'.format(model_name + '-mr'))
    links = list(map(gitlab_link, chain.from_iterable(list(project_sources.values()))))
    description = 'slot for testing {}, based on {}'.format(
        ', '.join(links), model_slot.name)
    test_slot = clone_slot(ref_slot, model_name + '-mr',
                           'MR test ' + description, platforms)
    if not merge:
        set_last_commits(test_slot, ref_date, commits)
    else:
        repos = slot_repos(test_slot)
        for name, commit in list(commits.items()):
            repos[name].checkout_opts['commit'] = commit
        for name, mrs in list(merges.items()):
            repos[name].checkout_opts['merges'] = mrs

    requested_projects = sorted(project_sources.keys())
    ref_slot.metadata['ci_test'] = {
        'is_reference': True,
    }
    test_slot.metadata['ci_test'] = {
        'is_test': True,
        'requested_projects': requested_projects
    }
    return ref_slot, test_slot


@slot_factory
def make_mr_slots(config, model_slots):
    '''
    Create reference and testing slot for some merge requests

    @param config: Configuration speciftying the new slots and where
                   feedback should go.

    An example of `config` is
        {
        "sources": [
            "lhcb/Rec!1753"
        ],
        "trigger": {
            "merge_request_iid": 1753,
            "project_id": 401,
            "discussion_id": "d708ea762deae76f7d718eb0eefbc9b66c134190",
            "note_id": 2913001
        },
        "platforms": null,
        "merge": true,
        }

    '''
    logger.debug('make_mr_slots called with configuration\n' +
                 json.dumps(config, indent=2))
    if not config['sources']:
        raise ValueError('config["sources"] must contain at least one project')

    # Call the create_mr_slots main method
    ref_slot, test_slot = create_mr_slots(
        sources=config['sources'],
        platforms=config['platforms'],
        merge=config['merge'],
        model_slots=model_slots)
    # register trigger information.
    # Needed for the GitLab reply of the LHCbPR2HD ThroughputProfileHandler.py
    test_slot.metadata['ci_test']['trigger'] = config['trigger']
    ref_slot.metadata['ci_test']['trigger'] = config['trigger']
    return [ref_slot, test_slot]


def post_gitlab_feedback(ref_slot, test_slot, flavour, mr_slots_config):
    """Post feedback on GitLab using the build ids."""
    prefix = 'https://lhcb-nightlies.web.cern.ch/'
    ref_id = '{flavour}/{ref_slot}/{ref_build}'.format(
        flavour=flavour,
        ref_slot=ref_slot.name,
        ref_build=ref_slot.build_id,
    )
    test_id = '{flavour}/{test_slot}/{test_build}'.format(
        flavour=flavour,
        test_slot=test_slot.name,
        test_build=test_slot.build_id,
    )
    message = ('Started [reference]({prefix}/{ref_id}/) '
               'and [{mode} test]({prefix}/{test_id}/) '
               'builds. Once done, check the [comparison]'
               '({prefix}/compare?a={ref_id}&b={test_id})'
               ' of build and test results.').format(
                   prefix=prefix,
                   flavour=flavour,
                   ref_id=ref_id,
                   test_id=test_id,
                   mode=('integration'
                         if mr_slots_config['merge'] else 'branch'),
               )
    logger.info('GitLab feedback: {!r}'.format(message))
    if os.environ.get('GITLAB_TOKEN'):
        trigger_source = mr_slots_config['trigger']
        try:
            gitlab_server = _gitlabServer()
            project = gitlab_server.projects.get(trigger_source['project_id'])
            mr = project.mergerequests.get(trigger_source['merge_request_iid'])
            discussion = mr.discussions.get(trigger_source['discussion_id'])
            # reply to discussion
            discussion.notes.create({'body': message})
            # add a label to MR (creates a project label if not existing,
            # noop if already labeled)
            mr.labels.append('ci-test-triggered')
            mr.save()
        except gitlab.GitlabError as e:
            # never fail when feedback can't be posted
            logger.error('Could not post feedback to gitlab: ' + e.message)
            pass
